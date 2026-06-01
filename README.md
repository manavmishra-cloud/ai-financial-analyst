```markdown
  # 📈 ai-financial-analyst

  > Streamlit dashboard for AI-augmented financial data analysis. Combines traditional quantitative analytics with LLM-generated narrative insights to surface risk concentrations, performance
  attribution, and trading anomalies.

  ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
  ![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
  ![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white)
  ![License](https://img.shields.io/badge/license-MIT-green)

  ## What it does

  Upload financial data (broker statements, P&L reports, market data CSVs) and get a structured analytical breakdown alongside LLM-generated natural-language commentary. The goal is to surface
  insights that traditional dashboards miss — concentration risks, hidden correlations, anomalous trading patterns — without requiring you to write any analytical code.

  ## Demo

  [FILL: add screenshot or GIF of dashboard here. Save as docs/demo.png in the repo, then:]

  docs/demo.png

  ## Features

  - 📊 **Automatic statistical profiling** — distribution analysis, correlation matrices, anomaly detection
  - 🤖 **LLM commentary layer** — natural-language summaries of what the numbers actually show
  - ⚠️  **Risk assessment** — concentration risk, drawdown analysis, regime classification
  - 📈 **Trend detection** — multi-timeframe momentum and mean-reversion signals
  - 💡 **Recommendation engine** — actionable insights synthesized from quantitative signals
  - 📁 **Multi-format input** — CSV, Excel, JSON support

  ## Quick start

  ```bash
  git clone https://github.com/manavmishra-cloud/ai-financial-analyst.git
  cd ai-financial-analyst
  pip install -r requirements.txt

  # Pull the LLM model
  ollama pull llama3.2:3b

  # Run the dashboard
  streamlit run app.py

  Open the URL Streamlit gives you (typically http://localhost:8501), upload your financial CSV, and explore the analyses.

  Sample analyses

  [FILL: list 3-5 specific analysis types your tool actually performs. Examples:]

  - Position concentration: Flags portfolios with >25% allocation to a single asset or sector
  - Drawdown analysis: Identifies max drawdown periods and recovery times
  - Correlation breakdown: Surfaces unexpected correlations across holdings
  - Win/loss attribution: Decomposes P&L by strategy, timeframe, or asset class
  - Regime detection: Classifies market conditions and flags allocation mismatches

  Tech stack

  - Language: Python 3.10+
  - UI: Streamlit
  - Data: pandas, scikit-learn for statistical processing
  - LLM: Ollama (local inference)
  - Storage: SQLite (optional, for persistent analysis history)

  Roadmap

  - [ ] Multi-account portfolio aggregation
  - [ ] Real-time data integration via broker APIs (Zerodha Kite, Upstox)
  - [ ] Persistent analysis history with snapshot comparison
  - [ ] Export to PDF / Excel reports
  - [ ] Multi-asset class support (equities, options, futures, crypto)

  License

  MIT

  Contact

  Manav Mishra · LinkedIn · manavmishra260205@gmail.com
