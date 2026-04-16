from __future__ import annotations

from datetime import datetime

from app.config import AppConfig
from app.data.alternative_data import AlternativeDataClient
from app.data.macro_data import MacroDataClient
from app.data.market_data import MarketDataClient
from app.data.news_data import NewsClient
from app.engines.decision_engine import DecisionEngine
from app.engines.fundamental_engine import FundamentalEngine
from app.engines.macro_engine import MacroEngine
from app.engines.positioning_engine import PositioningEngine
from app.engines.sentiment_engine import SentimentEngine
from app.engines.technical_engine import TechnicalLiquidityEngine
from app.models import DailyResearchReport, Opportunity
from app.reports.render import persist_report, render_markdown
from app.utils.notifications import Notifier
from app.utils.storage import Storage


class ResearchSystem:
    def __init__(self, config: AppConfig):
        self.config = config
        self.config.bootstrap_dirs()

        self.market_client = MarketDataClient(config.lookback_days)
        self.macro_client = MacroDataClient(config.fred_api_key)
        self.alt_client = AlternativeDataClient()
        self.news_client = NewsClient()

        self.macro_engine = MacroEngine()
        self.positioning_engine = PositioningEngine()
        self.sentiment_engine = SentimentEngine()
        self.fundamental_engine = FundamentalEngine()
        self.technical_engine = TechnicalLiquidityEngine()
        self.decision_engine = DecisionEngine()

        self.storage = Storage(config.db_path)
        self.notifier = Notifier(config)

    def run_once(self) -> DailyResearchReport:
        etf_proxy = ["SPY", "QQQ", "IWM", "XLF", "XLK"]
        all_tickers = sorted(set(self.config.tickers + [self.config.benchmark] + etf_proxy))
        ohlcv = self.market_client.fetch_ohlcv(all_tickers)
        prices = self.market_client.extract_close(ohlcv)
        volumes = self.market_client.extract_volume(ohlcv)
        etf_prices = prices[[c for c in etf_proxy if c in prices.columns]] if not prices.empty else prices
        etf_volumes = volumes[[c for c in etf_proxy if c in volumes.columns]] if not volumes.empty else volumes

        macro_snapshot = self.macro_client.fetch_macro_snapshot()
        regime, macro_signal = self.macro_engine.analyze(macro_snapshot)

        cot_df = self.alt_client.fetch_cot_financial_futures()
        insider_df = self.alt_client.fetch_openinsider()

        opportunities: list[Opportunity] = []
        for ticker in self.config.tickers:
            fundamentals = self.market_client.fetch_fundamentals(ticker)
            news = self.news_client.fetch_news_for_ticker(ticker)

            positioning = self.positioning_engine.analyze(
                ticker=ticker,
                cot_df=cot_df,
                insider_df=insider_df,
                prices=prices,
                volumes=volumes,
                etf_prices=etf_prices,
                etf_volumes=etf_volumes,
            )
            sentiment = self.sentiment_engine.analyze(news)
            fundamental = self.fundamental_engine.analyze(fundamentals, regime.regime)
            technical = self.technical_engine.analyze(ticker, prices)

            composite, confidence, trace = self.decision_engine.score(
                macro=macro_signal,
                positioning=positioning,
                sentiment=sentiment,
                fundamental=fundamental,
                technical=technical,
            )
            rating = self.decision_engine.rating(composite, confidence)

            # Strict skepticism: force Hold on weak edge.
            if confidence < self.config.min_confidence_threshold or abs(composite) < 0.25:
                rating = "Hold"

            thesis = (
                f"{ticker}: regime {regime.regime}; flows {positioning.evidence.get('state', 'unknown')} with "
                f"sentiment inputs {sentiment.evidence.get('classification', 'unknown')}; asymmetric edge only if "
                f"composite remains above strict threshold after missing-data penalties."
            )

            opportunities.append(
                Opportunity(
                    ticker=ticker,
                    rating=rating,
                    confidence=confidence,
                    composite_score=composite,
                    macro_view=macro_signal.summary,
                    positioning_flows=positioning.summary,
                    sentiment=sentiment.summary,
                    fundamentals=fundamental.summary,
                    key_levels=technical.summary,
                    thesis=thesis,
                    decision_trace=trace,
                    engine_breakdown={
                        "macro": macro_signal,
                        "positioning": positioning,
                        "sentiment": sentiment,
                        "fundamental": fundamental,
                        "technical": technical,
                    },
                )
            )

        opportunities = sorted(opportunities, key=lambda x: (x.composite_score, x.confidence), reverse=True)

        # Hard cap: do not output > 3 BUY-side ideas.
        buys = [o for o in opportunities if o.rating in {"Major Buy", "Buy"}][:3]
        sells = [o for o in opportunities if o.rating in {"Major Sell", "Sell"}]

        shortlist = buys
        if len(shortlist) < self.config.max_ideas_per_report:
            shortlist.extend(sells[: max(0, self.config.max_ideas_per_report - len(shortlist))])
        shortlisted = shortlist[: self.config.max_ideas_per_report]

        benchmark_note = "Benchmark analysis unavailable"
        if self.config.benchmark in prices.columns and len(prices[self.config.benchmark].dropna()) > 50:
            s = prices[self.config.benchmark].dropna()
            trailing = s.iloc[-1] / s.iloc[-21] - 1 if len(s) > 21 else 0
            benchmark_note = f"{self.config.benchmark} 1M return: {trailing:.2%}. Regime: {regime.regime}."

        report = DailyResearchReport(
            created_at=datetime.utcnow(),
            benchmark=self.config.benchmark,
            benchmark_context=benchmark_note,
            macro_regime=regime.regime,
            macro_confidence=regime.confidence,
            macro_explanation=regime.summary,
            opportunities=shortlisted,
        )
        self.storage.save_report(report)
        md_path, _ = persist_report(report, self.config.reports_dir)

        msg = render_markdown(report)
        self.notifier.send_discord(msg)
        self.notifier.send_email(f"DAILY HEDGE FUND BRIEFING {report.created_at.date()}", msg)

        print(f"Generated report at {md_path}")
        return report
