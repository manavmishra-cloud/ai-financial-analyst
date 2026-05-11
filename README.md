# AI Financial Analyst

Upload financial data (CSV / Excel / JSON) and get an instant, AI-powered report:
insights, risk analysis, trend, prediction, and a BUY / HOLD / SELL recommendation.

## Features

- Loads CSV, Excel, and JSON financial data
- Auto-detects price and volume columns
- Computes price change %, volatility, MA20/MA50 trend, RSI(14)
- AI analysis with a 3-tier engine priority:
  1. Local Ollama (qwen3 / llama3) — keeps your data on-machine
  2. Anthropic Claude API — if `ANTHROPIC_API_KEY` is set
  3. Rule-based fallback — works with no AI at all
- Interactive Streamlit dashboard with price chart + moving averages
- One-click PDF report export

## Tech stack

Python · pandas · numpy · matplotlib · Streamlit · fpdf2 · Ollama · Anthropic SDK

## Setup

```bash
git clone https://github.com/YOURNAME/financial-analyst.git
cd financial-analyst

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env       # add ANTHROPIC_API_KEY if you want cloud fallback
```

## Run

```bash
source venv/bin/activate
streamlit run app.py
```

Then open <http://localhost:8501> and upload a file from `data/`.

## Project structure

```
financial_analyst/
├── app.py            Streamlit dashboard (entry point)
├── extractor.py      File loaders (CSV / Excel / JSON)
├── processor.py      Ratios, trend, RSI
├── analyzer.py       LLM analysis with multi-engine fallback
├── reporter.py       PDF report generation
├── requirements.txt  Pinned dependencies
├── .env.example      Template for API keys
├── data/             Input files (gitignored)
├── output/           Generated PDF reports (gitignored)
└── screenshots/      Dashboard screenshots for the README
```

## Notes

- `data/`, `output/`, and `.env` are gitignored — never commit proprietary
  trading data or API keys.
- For a public demo, use a public dataset (e.g. yfinance) rather than firm data.
