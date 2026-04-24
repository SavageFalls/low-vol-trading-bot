from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

import numpy as np
import pandas as pd
import yfinance as yf


class MarketDataClient:
    def fetch_ohlcv(self, tickers: Iterable[str], lookback_days: int) -> pd.DataFrame:
        end = datetime.utcnow().date() + timedelta(days=1)
        start = end - timedelta(days=lookback_days)
        try:
            data = yf.download(
                tickers=list(tickers),
                start=start.isoformat(),
                end=end.isoformat(),
                auto_adjust=True,
                progress=False,
                threads=True,
                group_by="ticker",
            )
            if not data.empty:
                return data
        except Exception:
            pass

        # offline fallback: synthetic random-walk OHLCV panel
        idx = pd.bdate_range(start=start, end=end)
        frames = {}
        for t in tickers:
            rng = np.random.default_rng(abs(hash(t)) % (2**32))
            rets = rng.normal(0.0003, 0.02, len(idx))
            close = 100 * (1 + pd.Series(rets, index=idx)).cumprod()
            open_ = close.shift(1).fillna(close.iloc[0])
            high = pd.concat([open_, close], axis=1).max(axis=1) * (1 + rng.uniform(0.0, 0.01, len(idx)))
            low = pd.concat([open_, close], axis=1).min(axis=1) * (1 - rng.uniform(0.0, 0.01, len(idx)))
            vol = rng.integers(5_00_000, 5_000_000, len(idx))
            frames[t] = pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol}, index=idx)

        return pd.concat(frames, axis=1)

    def fetch_spy(self, lookback_days: int) -> pd.Series:
        df = self.fetch_ohlcv(["SPY"], lookback_days)
        if isinstance(df.columns, pd.MultiIndex):
            close = df[("SPY", "Close")]
        else:
            close = df["Close"]
        return close.dropna()
