"""Generate a PDF report summarizing the analysis."""
import os
from datetime import datetime
from fpdf import FPDF


def _safe(text):
    """fpdf2 uses latin-1 by default — strip characters it can't encode."""
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_report(analysis, ratios, trend, rsi, ticker="STOCK"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 12, _safe(f"Financial Analysis - {ticker}"), ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, datetime.now().strftime("Generated: %Y-%m-%d %H:%M"), ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Key Metrics", ln=True)
    pdf.set_font("Arial", "", 11)
    rows = [
        ("Trend", trend),
        ("RSI", rsi if rsi is not None else "N/A"),
        ("Price Change", f"{ratios.get('price_change_pct', 'N/A')}%"),
        ("Volatility", ratios.get("volatility", "N/A")),
        ("Current Price", ratios.get("current_price", "N/A")),
        ("Avg Price", ratios.get("avg_price", "N/A")),
    ]
    for label, value in rows:
        pdf.cell(0, 7, _safe(f"{label}: {value}"), ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI Analysis", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, _safe(analysis))

    os.makedirs("output", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"output/{ticker}_report_{stamp}.pdf"
    pdf.output(path)
    return path
