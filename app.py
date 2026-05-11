"""AI Financial Analyst — Streamlit dashboard.

Run with:
    streamlit run app.py
"""
import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from extractor import load_file, get_summary
from schema import infer_schema, describe_schema
from processor import calculate_ratios, detect_trend, calculate_rsi
from analyzer import analyze
from reporter import generate_report


st.set_page_config(page_title="AI Financial Analyst", page_icon="📈", layout="wide")

st.title("AI Financial Analyst")
st.caption("Upload financial data → get insights, risk, trend, prediction, and BUY/HOLD/SELL.")

with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Stock / company label", value="STOCK")
    st.markdown("**Engine priority**")
    st.markdown("1. Local Ollama (qwen3/llama3)\n2. Anthropic Claude API\n3. Rule-based fallback")
    st.markdown("---")
    st.caption("Place your data in `data/` or upload below.")

uploaded = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "xls", "json"])

if not uploaded:
    st.info("👆 Upload a file to begin. The dashboard auto-detects column roles so any naming convention works.")
    st.stop()

# Save upload to temp file so the extractor can route on file extension.
suffix = os.path.splitext(uploaded.name)[1]
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    tmp.write(uploaded.getvalue())
    tmp_path = tmp.name

try:
    df = load_file(tmp_path)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(20), use_container_width=True)


@st.cache_data(show_spinner="Detecting columns...")
def _cached_schema(file_bytes, columns_tuple):
    """Cache per upload so we don't re-call the LLM on every interaction."""
    return infer_schema(df)


detected = _cached_schema(uploaded.getvalue(), tuple(df.columns))

with st.expander(f"🔍 Detected schema: {describe_schema(detected)} — click to override", expanded=False):
    st.caption(
        "If a role is wrong, pick the right column from its dropdown. "
        "Choose `(none)` to remove it."
    )
    col_options = ["(none)"] + list(df.columns)
    schema = dict(detected)
    cols = st.columns(2)
    for i, role in enumerate(["price", "volume", "timestamp", "ticker", "bid", "ask"]):
        with cols[i % 2]:
            current = detected.get(role)
            idx = col_options.index(current) if current in col_options else 0
            choice = st.selectbox(f"`{role}` column", options=col_options, index=idx, key=f"sel_{role}")
            if choice != "(none)":
                schema[role] = choice
            elif role in schema:
                schema.pop(role)

ratios = calculate_ratios(df, schema=schema)
trend = detect_trend(df, schema=schema)
rsi = calculate_rsi(df, schema=schema)
summary = get_summary(df)

st.subheader("Key metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Trend", trend)
c2.metric("RSI", rsi if rsi is not None else "—")
c3.metric("Price change", f"{ratios.get('price_change_pct', 0)}%")
c4.metric("Volatility", ratios.get("volatility", "—"))

price_col = schema.get("price")
if price_col and price_col in df.columns:
    st.subheader(f"Price chart — column `{price_col}`")
    prices = pd.to_numeric(df[price_col], errors="coerce")
    fig, ax = plt.subplots(figsize=(12, 4))
    prices.plot(ax=ax, color="#1f77b4", linewidth=1.2, label=price_col)
    if len(prices.dropna()) >= 20:
        prices.rolling(20).mean().plot(ax=ax, color="orange", linestyle="--", label="MA20")
    if len(prices.dropna()) >= 50:
        prices.rolling(50).mean().plot(ax=ax, color="red", linestyle="--", label="MA50")
    ax.legend()
    ax.set_title(f"{ticker} — price movement")
    ax.set_xlabel("Row index")
    ax.set_ylabel("Price")
    st.pyplot(fig)
else:
    st.info("No price column detected for this file — skipping chart. AI analysis will still run on the raw structure.")

st.subheader("AI analysis")
sample_text = df.head(5).to_string()
try:
    describe_text = df.describe(include="all").to_string()
except Exception:
    describe_text = ""
with st.spinner("Running analysis — qwen3 thinking models can take 30-90s..."):
    analysis_text = analyze(summary, ratios, trend, rsi, sample=sample_text, describe=describe_text)
st.markdown(analysis_text)

st.subheader("Export")
if st.button("Generate PDF report"):
    with st.spinner("Building PDF..."):
        pdf_path = generate_report(analysis_text, ratios, trend, rsi, ticker)
    with open(pdf_path, "rb") as f:
        st.download_button(
            "Download PDF",
            data=f.read(),
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
        )
    st.success(f"Saved to {pdf_path}")

try:
    os.unlink(tmp_path)
except Exception:
    pass
