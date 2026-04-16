from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

import pandas as pd
import yfinance as yf


class MarketDataClient:
    def __init__(self, lookback_days: int = 252):
        self.lookback_days = lookback_days

    def fetch_ohlcv(self, tickers: Iterable[str]) -> pd.DataFrame:
        end = datetime.utcnow().date() + timedelta(days=1)
        start = end - timedelta(days=self.lookback_days * 2)
        data = yf.download(
            list(tickers),
            start=start.isoformat(),
            end=end.isoformat(),
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        return data.dropna(how="all") if not data.empty else pd.DataFrame()

    def extract_close(self, ohlcv: pd.DataFrame) -> pd.DataFrame:
        if ohlcv.empty:
            return pd.DataFrame()
        if "Close" in ohlcv.columns:
            px = ohlcv["Close"]
        else:
            px = ohlcv
        if isinstance(px, pd.Series):
            px = px.to_frame()
        return px.dropna(how="all")

    def extract_volume(self, ohlcv: pd.DataFrame) -> pd.DataFrame:
        if ohlcv.empty or "Volume" not in ohlcv.columns:
            return pd.DataFrame()
        vol = ohlcv["Volume"]
        if isinstance(vol, pd.Series):
            vol = vol.to_frame()
        return vol.dropna(how="all")

    def fetch_fundamentals(self, ticker: str) -> dict:
        info = yf.Ticker(ticker).info
        return {
            "marketCap": info.get("marketCap"),
            "forwardPE": info.get("forwardPE"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "profitMargins": info.get("profitMargins"),
            "debtToEquity": info.get("debtToEquity"),
            "returnOnEquity": info.get("returnOnEquity"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        }
