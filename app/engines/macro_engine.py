from __future__ import annotations

import numpy as np
import pandas as pd


class MacroEngine:
    def analyze(self, macro_df: pd.DataFrame) -> dict:
        clean = macro_df.sort_index().ffill().dropna(how="all")
        if clean.empty:
            return {"score": 0.0, "regime": "mixed", "summary": "Macro data unavailable; using neutral regime."}

        latest = clean.iloc[-1]
        trailing = clean.iloc[-12:] if len(clean) >= 12 else clean

        cpi_trend = trailing["cpi"].pct_change(12).iloc[-1] if "cpi" in trailing and len(trailing) > 12 else 0
        yc = float(latest.get("10y", 0) - latest.get("2y", 0))
        hy = float(latest.get("high_yield_spread", 5.0))
        fci = float(latest.get("financial_conditions", 0.0))

        score = 0.0
        reasons = []

        if cpi_trend < 0.03:
            score += 0.25
            reasons.append("Inflation trend cooling.")
        else:
            score -= 0.2
            reasons.append("Inflation remains sticky.")

        if yc > 0:
            score += 0.2
            reasons.append("Yield curve is positive (risk-on support).")
        else:
            score -= 0.2
            reasons.append("Yield curve inversion signals caution.")

        if hy < 5.5:
            score += 0.25
            reasons.append("Credit spreads supportive.")
        else:
            score -= 0.25
            reasons.append("Credit stress elevated.")

        if fci < 0:
            score += 0.2
            reasons.append("Financial conditions relatively loose.")
        else:
            score -= 0.2
            reasons.append("Financial conditions tightening.")

        score = float(np.clip(score, -1, 1))
        regime = "risk_on" if score > 0.2 else "risk_off" if score < -0.2 else "mixed"
        return {
            "score": score,
            "regime": regime,
            "summary": " ".join(reasons),
        }
