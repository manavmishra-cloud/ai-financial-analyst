"""Send data to an LLM for analysis. Order of preference:
1. Local Ollama (qwen3 -> llama3 -> any installed model)
2. Anthropic Claude API (if ANTHROPIC_API_KEY is set)
3. Rule-based fallback (no AI required)
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434"
PREFERRED_MODELS = ["qwen3:30b", "qwen3", "llama3", "qwen2.5", "mistral"]


def build_prompt(summary, ratios, trend, rsi, sample="", describe=""):
    extras = ""
    if sample:
        extras += f"\n\nDATA SAMPLE (first 5 rows):\n{sample}"
    if describe:
        extras += f"\n\nDESCRIBE STATS:\n{describe}"

    return f"""You are a senior quant trading analyst.
Analyze the following data and produce a structured report.

TREND: {trend}
RSI: {rsi} (above 70 = overbought, below 30 = oversold)
KEY RATIOS:
{json.dumps(ratios, indent=2)}
DATA SUMMARY: rows={summary.get('rows')}, columns={summary.get('columns')}{extras}

Return your report with exactly these 5 sections:
1. INSIGHTS — 3 specific observations using the numbers above
2. RISK ANALYSIS — top 3 risks given the current state
3. TREND ANALYSIS — explain the direction with evidence (price if available,
   otherwise reason about the data columns shown)
4. PREDICTION — short-term outlook
5. RECOMMENDATION — BUY, HOLD or SELL with a confidence % and one-line reason.
   If this is not market price data (e.g. an income statement), instead give a
   POSITIVE / NEUTRAL / NEGATIVE outlook with reasoning.

Be concise and professional. Cite numbers wherever possible."""


def pick_ollama_model():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code != 200:
            return None
        installed = [m["name"] for m in r.json().get("models", [])]
        for pref in PREFERRED_MODELS:
            for name in installed:
                if pref in name:
                    return name
        return installed[0] if installed else None
    except Exception:
        return None


def analyze_with_ollama(model, prompt):
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json().get("response", "")


def analyze_with_anthropic(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def rule_based(ratios, trend, rsi):
    signal = "HOLD"
    reasons = []

    if trend == "UPTREND":
        signal = "BUY"
        reasons.append("Price MA20 > MA50 — uptrend confirmed")
    elif trend == "DOWNTREND":
        signal = "SELL"
        reasons.append("Price MA20 < MA50 — downtrend confirmed")

    if rsi is not None:
        if rsi < 30:
            signal = "BUY"
            reasons.append(f"RSI={rsi} — oversold, possible bounce")
        elif rsi > 70:
            signal = "SELL"
            reasons.append(f"RSI={rsi} — overbought, possible pullback")

    change = ratios.get("price_change_pct", 0)
    if change > 5:
        reasons.append(f"Strong positive move of {change}%")
    elif change < -5:
        reasons.append(f"Strong negative move of {change}%")

    if not reasons:
        reasons.append("No strong signals — recommend HOLD and monitor")

    body = "\n".join(f"- {r}" for r in reasons)
    return (
        f"5. RECOMMENDATION: {signal} (rule-based, low confidence)\n\n"
        f"REASONS:\n{body}\n\n"
        f"NOTE: No LLM available. Install Ollama (`ollama pull llama3`) "
        f"or set ANTHROPIC_API_KEY in .env for full AI analysis."
    )


def analyze(summary, ratios, trend, rsi, sample="", describe=""):
    prompt = build_prompt(summary, ratios, trend, rsi, sample=sample, describe=describe)

    model = pick_ollama_model()
    if model:
        try:
            text = analyze_with_ollama(model, prompt)
            return f"[Engine: Ollama / {model}]\n\n{text}"
        except Exception as e:
            print(f"Ollama failed: {e}")

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            text = analyze_with_anthropic(prompt)
            return f"[Engine: Anthropic Claude]\n\n{text}"
        except Exception as e:
            print(f"Anthropic failed: {e}")

    return f"[Engine: rule-based fallback]\n\n{rule_based(ratios, trend, rsi)}"
