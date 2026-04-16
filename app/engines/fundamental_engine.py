from __future__ import annotations

import numpy as np

from app.models import EngineSignal


class FundamentalEngine:
    def analyze(self, fundamentals: dict, macro_regime: str) -> EngineSignal:
        if not fundamentals:
            return EngineSignal(-0.25, 0.2, "Fundamentals unknown: no data returned.", {})

        growth = fundamentals.get("revenueGrowth")
        earnings = fundamentals.get("earningsGrowth")
        margins = fundamentals.get("profitMargins")
        roe = fundamentals.get("returnOnEquity")
        dte = fundamentals.get("debtToEquity")
        fpe = fundamentals.get("forwardPE")

        missing = sum(v is None for v in [growth, earnings, margins, roe, dte, fpe])
        growth = growth or 0.0
        earnings = earnings or 0.0
        margins = margins or 0.0
        roe = roe or 0.0
        dte = dte if dte is not None else 130.0
        fpe = fpe if fpe is not None else 38.0

        quality = np.clip(0.35 * growth + 0.25 * earnings + 0.20 * margins + 0.20 * roe, -1, 1)
        valuation = np.clip((22 - fpe) / 25, -1, 1)
        leverage = np.clip((80 - dte) / 120, -1, 1)

        regime_bias = 0.0
        if "risk_off" in macro_regime:
            regime_bias = 0.08 * np.sign(valuation) + 0.06 * np.sign(leverage)
        if "risk_on" in macro_regime:
            regime_bias += 0.08 * np.sign(growth + earnings)

        score = float(np.clip(0.55 * quality + 0.25 * valuation + 0.20 * leverage + regime_bias - 0.08 * missing, -1, 1))
        confidence = float(np.clip(0.75 - 0.1 * missing, 0.25, 0.82))
        summary = (
            f"Growth={growth:.2f}, Earnings={earnings:.2f}, Margin={margins:.2f}, ROE={roe:.2f}, "
            f"ForwardPE={fpe:.1f}, DebtToEquity={dte:.1f}, missing_fields={missing}."
        )
        return EngineSignal(
            score=score,
            confidence=confidence,
            summary=summary,
            evidence={
                "growth": growth,
                "earnings": earnings,
                "margin": margins,
                "roe": roe,
                "forwardPE": fpe,
                "debtToEquity": dte,
                "missing_fields": missing,
            },
        )
