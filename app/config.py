from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Settings:
    tickers: List[str] = field(
        default_factory=lambda: os.getenv(
            "ANALYST_TICKERS",
            "AAPL,MSFT,AMZN,NVDA,GOOGL,META,TSLA,UNH,JPM,XOM,LLY,AVGO,HD,COST,PG,WMT,MRK,JNJ,CRM,AMD",
        ).split(",")
    )
    db_path: str = os.getenv("ANALYST_DB_PATH", "research_analyst.db")
    report_dir: str = os.getenv("ANALYST_REPORT_DIR", "reports")
    lookback_days: int = int(os.getenv("ANALYST_LOOKBACK_DAYS", "260"))
    min_confidence_to_notify: float = float(os.getenv("ANALYST_MIN_CONFIDENCE", "0.72"))
    max_ideas_per_run: int = int(os.getenv("ANALYST_MAX_IDEAS", "5"))

    # notification settings
    discord_webhook_url: str | None = os.getenv("DISCORD_WEBHOOK_URL")
    smtp_host: str | None = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    email_to: str | None = os.getenv("EMAIL_TO")
    email_from: str | None = os.getenv("EMAIL_FROM")

    # macro symbols
    fred_series: Dict[str, str] = field(
        default_factory=lambda: {
            "fed_funds": "FEDFUNDS",
            "cpi": "CPIAUCSL",
            "unemployment": "UNRATE",
            "financial_conditions": "NFCI",
            "2y": "DGS2",
            "10y": "DGS10",
            "high_yield_spread": "BAMLH0A0HYM2",
        }
    )


def get_settings() -> Settings:
    return Settings()
