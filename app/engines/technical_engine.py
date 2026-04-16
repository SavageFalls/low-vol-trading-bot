from __future__ import annotations

import numpy as np
import pandas as pd

from app.models import EngineSignal


class TechnicalLiquidityEngine:
    def analyze(self, ticker: str, prices: pd.DataFrame) -> EngineSignal:
        if ticker not in prices.columns:
            return EngineSignal(-0.2, 0.2, "Technicals unknown: price series missing.", {})

        s = prices[ticker].dropna()
        if len(s) < 120:
            return EngineSignal(-0.2, 0.25, "Technicals weak: insufficient lookback window.", {})

        r = s.pct_change().dropna()
        ma20 = float(s.rolling(20).mean().iloc[-1])
        ma50 = float(s.rolling(50).mean().iloc[-1])
        ma200 = float(s.rolling(200).mean().iloc[-1]) if len(s) >= 200 else float(s.rolling(120).mean().iloc[-1])
        last = float(s.iloc[-1])

        resistance = float(s.rolling(60).max().iloc[-2])
        support = float(s.rolling(60).min().iloc[-2])
        breakout = last > resistance
        breakdown = last < support

        trend = 0.5 * np.sign(last - ma50) + 0.5 * np.sign(ma50 - ma200)
        range_signal = 0.9 if breakout else (-0.9 if breakdown else 0.0)
        ann_vol = float(r.rolling(20).std().iloc[-1] * np.sqrt(252))
        vol_penalty = float(np.clip((ann_vol - 0.45) / 0.40, 0, 1))

        score = float(np.clip(0.55 * trend + 0.45 * range_signal - 0.30 * vol_penalty, -1, 1))
        summary = (
            f"MA20={ma20:.2f}, MA50={ma50:.2f}, MA200={ma200:.2f}; support={support:.2f}, resistance={resistance:.2f}, "
            f"price={last:.2f}, breakout={breakout}, breakdown={breakdown}, ann_vol={ann_vol:.2f}."
        )

        return EngineSignal(
            score=score,
            confidence=0.74,
            summary=summary,
            evidence={
                "ma20": ma20,
                "ma50": ma50,
                "ma200": ma200,
                "support": support,
                "resistance": resistance,
                "price": last,
                "breakout": str(breakout),
                "breakdown": str(breakdown),
                "ann_vol": ann_vol,
            },
        )
