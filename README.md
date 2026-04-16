# Autonomous AI Research Analyst Agent

Production-style, multi-engine **daily hedge fund briefing** system for paper trading. It runs autonomously, ingests free data, scores opportunities skeptically, and outputs only high-conviction ideas.

## Updated Architecture

### 1) Macro Intelligence Engine
- Inputs: FRED inflation trend, fed funds + 6M delta, yield curve, financial conditions, liquidity (M2).
- Output: regime label (`risk_on_*`, `risk_off_*`, `balanced_*`) + confidence.

### 2) Positioning & Flow Engine
- Inputs:
  - COT net asset-manager positioning
  - Insider buying/selling balance (OpenInsider)
  - ETF flow proxy from dollar-volume pressure on SPY/QQQ/IWM/XLF/XLK
  - Unusual volume spikes on each equity
- Output: `accumulation`, `distribution`, or `neutral`.

### 3) Sentiment Engine (real data driven)
- Inputs: RSS news headlines (Yahoo Finance ticker feed + MarketWatch + CNBC).
- Output: bullish/bearish/neutral + narrative-shift score and confidence.

### 4) Fundamental Engine
- Inputs: growth, earnings, margins, ROE, valuation, leverage.
- Output: regime-aware fundamental score with missing-data penalties.

### 5) Technical Engine
- Inputs: MA20/MA50/MA200 trend, breakout/breakdown, support/resistance, realized volatility.
- Output: technical conviction score + key levels.

### 6) Decision Engine (strict)
- Fixed weights:
  - Macro 30%
  - Flows 25%
  - Sentiment 20%
  - Fundamentals 15%
  - Technicals 10%
- Strict filtering:
  - heavy penalties for missing/weak confidence
  - explicit conflict penalties
  - forced neutrality for weak edge
  - **max 3 Buy-side ideas per report**

## Autonomy
- Scheduled weekday pre-/post-market runs via APScheduler.
- CLI command for autonomous mode:

```bash
python -m app.scheduler
```

- One-off run:

```bash
python main.py run-once
```

Reports are saved into:
- `reports/daily_report_*.md`
- `reports/daily_report_*.json`

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FRED_API_KEY="..."
export ANALYST_TICKERS="AAPL,MSFT,NVDA,AMZN,GOOGL,META"
export BENCHMARK="SPY"
export MIN_CONFIDENCE="0.66"
```

Optional notifications:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="you@example.com"
export SMTP_PASSWORD="app-password"
export EMAIL_FROM="you@example.com"
export EMAIL_TO="you@example.com"
```

## Example Daily Report Format

```text
## DAILY HEDGE FUND BRIEFING

### Macro Regime
- Regime: risk_on_easing
- Confidence: 0.78
- View: Inflation decelerating while financial conditions remain supportive...

### Top Conviction Ideas (MAX 3)

Ticker: NVDA
Rating: Buy
Confidence: 0.77

Macro View: ...
Positioning & Flows: ...
Sentiment: ...
Fundamentals: ...
Technical Levels: ...
Thesis: ...

Decision Trace:
macro=+0.120, flows=+0.090, sentiment=+0.030, fundamentals=+0.050, technicals=+0.025, missing_penalty=0.000, conflict_penalty=0.000, total=+0.315
```

## Notes
- This is for research/paper-trading workflows only.
- Not investment advice.
