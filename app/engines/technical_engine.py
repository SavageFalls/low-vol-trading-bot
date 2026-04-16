from __future__ import annotations

import numpy as np
import pandas as pd


class TechnicalEngine:
    def analyze(self, ticker_df: pd.DataFrame) -> dict:
        close = ticker_df["Close"].dropna()
        if len(close) < 100:
            return {"score": 0.0, "summary": "Not enough price history.", "levels": {}}

        ret = close.pct_change().dropna()
        vol20 = float(ret.rolling(20).std().iloc[-1] * (252 ** 0.5))
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        px = float(close.iloc[-1])
        y_high = float(close.rolling(252).max().iloc[-1])
        y_low = float(close.rolling(252).min().iloc[-1])

        score = 0.0
        notes = []

        if px > ma50 > ma200:
            score += 0.35
            notes.append("Uptrend confirmed (price > MA50 > MA200).")
        elif px < ma50 < ma200:
            score -= 0.35
            notes.append("Downtrend confirmed.")

        if vol20 < 0.32:
            score += 0.1
            notes.append("Realized volatility contained.")
        else:
            score -= 0.1
            notes.append("Realized volatility elevated.")

        dist_to_high = (y_high - px) / max(1e-6, y_high)
        if dist_to_high < 0.05:
            score += 0.1
            notes.append("Near breakout zone.")

        levels = {
            "last": round(px, 2),
            "ma50": round(ma50, 2),
            "ma200": round(ma200, 2),
            "52w_high": round(y_high, 2),
            "52w_low": round(y_low, 2),
        }

        return {"score": float(np.clip(score, -1, 1)), "summary": " ".join(notes), "levels": levels}
