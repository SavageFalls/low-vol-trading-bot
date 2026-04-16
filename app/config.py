from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class AppConfig:
    tickers: List[str] = field(
        default_factory=lambda: [
            "AAPL",
            "MSFT",
            "NVDA",
            "AMZN",
            "GOOGL",
            "META",
            "TSLA",
            "JPM",
            "XOM",
            "UNH",
            "LLY",
            "COST",
            "AVGO",
            "PG",
            "JNJ",
            "HD",
            "KO",
            "MRK",
            "PFE",
            "AMD",
        ]
    )
    benchmark: str = "SPY"
    lookback_days: int = 252
    min_confidence_threshold: float = 0.66
    max_ideas_per_report: int = 3
    data_dir: Path = Path("data")
    reports_dir: Path = Path("reports")
    db_path: Path = Path("data/research.db")

    fred_api_key: str | None = None
    discord_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_to: str | None = None

    pre_market_hour_utc: int = 12
    post_market_hour_utc: int = 21

    @classmethod
    def from_env(cls) -> "AppConfig":
        tickers = os.getenv("ANALYST_TICKERS")
        return cls(
            tickers=[t.strip().upper() for t in tickers.split(",")] if tickers else cls().tickers,
            benchmark=os.getenv("BENCHMARK", "SPY").upper(),
            lookback_days=int(os.getenv("LOOKBACK_DAYS", "252")),
            min_confidence_threshold=float(os.getenv("MIN_CONFIDENCE", "0.66")),
            max_ideas_per_report=min(3, int(os.getenv("MAX_IDEAS", "3"))),
            fred_api_key=os.getenv("FRED_API_KEY"),
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            email_from=os.getenv("EMAIL_FROM"),
            email_to=os.getenv("EMAIL_TO"),
            pre_market_hour_utc=int(os.getenv("PRE_MARKET_HOUR_UTC", "12")),
            post_market_hour_utc=int(os.getenv("POST_MARKET_HOUR_UTC", "21")),
        )

    def bootstrap_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
