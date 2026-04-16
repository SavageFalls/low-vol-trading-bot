from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pandas as pd

from app.config import Settings
from app.data.macro_data import MacroDataClient
from app.data.market_data import MarketDataClient
from app.data.news_data import NewsClient
from app.data.positioning_data import PositioningDataClient
from app.decision_engine import DecisionEngine
from app.engines.fundamental_engine import FundamentalEngine
from app.engines.macro_engine import MacroEngine
from app.engines.positioning_engine import PositioningEngine
from app.engines.sentiment_engine import SentimentEngine
from app.engines.technical_engine import TechnicalEngine
from app.notifications import Notifier
from app.reporting import write_report
from app.storage import Storage


class ResearchAnalystApp:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.market = MarketDataClient()
        self.macro_data = MacroDataClient()
        self.positioning_data = PositioningDataClient()
        self.news = NewsClient()

        self.macro_engine = MacroEngine()
        self.positioning_engine = PositioningEngine()
        self.sentiment_engine = SentimentEngine()
        self.fundamental_engine = FundamentalEngine()
        self.technical_engine = TechnicalEngine()
        self.decision_engine = DecisionEngine()

        self.storage = Storage(settings.db_path)
        self.notifier = Notifier(settings)

    def run_once(self, run_type: str = "daily") -> Dict:
        macro_df = self.macro_data.fetch_fred_series(self.settings.fred_series)
        macro_signal = self.macro_engine.analyze(macro_df)

        ohlcv = self.market.fetch_ohlcv(self.settings.tickers, self.settings.lookback_days)

        try:
            cot = self.positioning_data.fetch_cot_financial_futures()
        except Exception:
            cot = pd.DataFrame()

        ideas: List[Dict] = []
        for ticker in self.settings.tickers:
            ticker_df = self._extract_ticker_df(ohlcv, ticker)
            if ticker_df.empty:
                continue

            news_items = self.news.fetch_rss(ticker)
            try:
                insider = self.positioning_data.fetch_openinsider(ticker)
            except Exception:
                insider = pd.DataFrame()

            signals = {
                "macro": macro_signal,
                "positioning": self.positioning_engine.analyze(cot, insider),
                "sentiment": self.sentiment_engine.analyze(news_items),
                "fundamental": self.fundamental_engine.analyze(ticker, macro_signal["regime"]),
                "technical": self.technical_engine.analyze(ticker_df),
            }

            d = self.decision_engine.evaluate(signals)
            idea = {
                "ticker": ticker,
                "score": d.score,
                "confidence": d.confidence,
                "rating": d.rating,
                "macro_summary": signals["macro"]["summary"],
                "positioning_summary": signals["positioning"]["summary"],
                "sentiment_summary": signals["sentiment"]["summary"],
                "fundamental_summary": signals["fundamental"]["summary"],
                "levels": signals["technical"].get("levels", {}),
                "thesis": self._build_thesis(ticker, signals, d),
                "rationale": d.rationale,
            }
            ideas.append(idea)

        ranked = sorted(
            ideas,
            key=lambda x: (x["rating"] in ["Major Buy", "Buy"], x["confidence"], x["score"]),
            reverse=True,
        )
        filtered = [
            i for i in ranked if i["rating"] in ["Major Buy", "Buy"] and i["confidence"] >= self.settings.min_confidence_to_notify
        ][: self.settings.max_ideas_per_run]

        if not filtered:
            filtered = ranked[: min(3, len(ranked))]

        report_path = write_report(self.settings.report_dir, run_type, filtered, macro_signal)
        run_ts = datetime.utcnow().isoformat()
        self.storage.save_ideas(run_ts, filtered, report_path)

        notif = f"[{run_type}] {len(filtered)} top ideas generated. Report: {report_path}"
        self.notifier.notify(notif)
        return {"run_ts": run_ts, "report_path": report_path, "ideas": filtered, "macro": macro_signal}

    def _extract_ticker_df(self, ohlcv: pd.DataFrame, ticker: str) -> pd.DataFrame:
        if isinstance(ohlcv.columns, pd.MultiIndex):
            if ticker in ohlcv.columns.get_level_values(0):
                return ohlcv[ticker].dropna()
            return pd.DataFrame()
        return ohlcv.dropna()

    def _build_thesis(self, ticker: str, signals: Dict, decision) -> str:
        return (
            f"{ticker}: Top-down score {decision.score:.2f}. Macro regime={signals['macro']['regime']} with "
            f"positioning {signals['positioning']['score']:.2f}, sentiment {signals['sentiment']['score']:.2f}, "
            f"fundamentals {signals['fundamental']['score']:.2f}, and technicals {signals['technical']['score']:.2f}."
        )
