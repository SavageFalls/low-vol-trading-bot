# AI-Powered Hedge Fund Research Analyst (Standalone)

A modular, multi-agent stock research system that runs proactively (pre-market, post-market, and weekend macro review), ranks opportunities, writes daily hedge fund briefings, and can send notifications without user prompts.

## System Architecture

### Agent Graph
1. **Macro Intelligence Engine** (FRED): identifies regime (`risk_on`, `mixed`, `risk_off`) from inflation trend, yield curve, credit spreads, and financial conditions.
2. **Positioning & Flow Engine** (CFTC COT + OpenInsider scraping): detects crowded vs under-owned positioning and insider net buying/selling.
3. **Sentiment Engine** (Yahoo Finance RSS): parses headlines and applies a contrarian sentiment adjustment.
4. **Fundamental Engine** (`yfinance` fundamentals): evaluates growth, margin quality, valuation, and leverage with macro-aware context.
5. **Technical & Liquidity Engine** (`yfinance` prices): trend structure, realized vol, and breakout proximity.
6. **Decision Engine**: dynamic weighted synthesis, explicit conflict penalties, conservative rating mapping.

### Thinking Order (Top-Down)
`Macro -> Positioning -> Sentiment -> Fundamentals -> Technicals -> Decision`

Conflicts (e.g., bearish macro + bullish technicals) are penalized in confidence/score to avoid overconfident calls.

## Features
- Automated scans with built-in Python scheduler loop
- SQLite persistence of ideas and run history
- Markdown report generation in `/reports`
- Discord + SMTP notification hooks
- Conservative Major Buy/Major Sell thresholds

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Single run:
```bash
python -m app.scheduler --once
```

Background scheduler loop:
```bash
python -m app.scheduler
```

## Environment Variables

```bash
ANALYST_TICKERS=AAPL,MSFT,NVDA,AMZN,GOOGL,META
ANALYST_DB_PATH=research_analyst.db
ANALYST_REPORT_DIR=reports
ANALYST_LOOKBACK_DAYS=260
ANALYST_MIN_CONFIDENCE=0.72
ANALYST_MAX_IDEAS=5

DISCORD_WEBHOOK_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
EMAIL_TO=
```

## Output Schema (per idea)
- Ticker
- Macro View
- Positioning & Flows
- Sentiment
- Key Levels
- Thesis
- Rating (Major Buy / Buy / Hold / Sell / Major Sell)
- Confidence

## Example Daily Briefing (abridged)

```text
Ticker: NVDA
Macro View: Inflation cooling, spreads supportive, mixed-to-risk-on backdrop.
Positioning & Flows: Spec positioning extended, but insider activity neutral.
Sentiment: Euphoric headlines -> contrarian adjustment.
Key Levels: Last 912.2, MA50 881.1, MA200 701.5, 52wH 974.0, 52wL 415.2
Thesis: Macro supportive, strong earnings quality, trend intact; sentiment crowded reduces conviction.
Rating: Buy
Confidence: 0.78
```

## Upgrade Path
- Add walk-forward paper-trading portfolio construction with risk budgeting.
- Add feature store and performance attribution for each engine.
- Add reinforcement/meta-learning to update engine weights based on out-of-sample hit rate.
- Add SEC filings parser and earnings-call transcript NLP.
- Add Bayesian regime model and volatility targeting.
