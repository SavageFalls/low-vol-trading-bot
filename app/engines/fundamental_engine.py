from __future__ import annotations

import numpy as np
import yfinance as yf


class FundamentalEngine:
    def analyze(self, ticker: str, macro_regime: str) -> dict:
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            info = {}
        score = 0.0
        notes = []

        pe = info.get("forwardPE")
        growth = info.get("earningsQuarterlyGrowth")
        margin = info.get("profitMargins")
        debt_to_equity = info.get("debtToEquity")

        if growth is not None:
            if growth > 0.12:
                score += 0.2
                notes.append("Earnings growth healthy.")
            elif growth < 0:
                score -= 0.2
                notes.append("Negative earnings growth.")

        if margin is not None:
            if margin > 0.15:
                score += 0.15
                notes.append("Profitability strong.")
            elif margin < 0.05:
                score -= 0.1
                notes.append("Margin profile weak.")

        if pe is not None:
            if macro_regime == "risk_off" and pe > 35:
                score -= 0.15
                notes.append("High valuation in defensive macro regime.")
            elif macro_regime == "risk_on" and pe < 25:
                score += 0.1
                notes.append("Reasonable valuation for risk-on regime.")

        if debt_to_equity is not None and debt_to_equity > 180:
            score -= 0.1
            notes.append("Leverage elevated.")

        return {"score": float(np.clip(score, -1, 1)), "summary": " ".join(notes) or "Fundamentals neutral."}
