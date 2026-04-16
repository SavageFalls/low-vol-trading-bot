from __future__ import annotations

import numpy as np

from app.models import EngineSignal, MarketRegime


class MacroEngine:
    def analyze(self, macro_snapshot: dict) -> tuple[MarketRegime, EngineSignal]:
        if not macro_snapshot:
            regime = MarketRegime(
                regime="unknown",
                score=0.0,
                confidence=0.25,
                summary="Macro data unavailable (missing FRED API key or failed fetch).",
                evidence={},
            )
            return regime, EngineSignal(0.0, 0.25, regime.summary, {})

        cpi = macro_snapshot["cpi_yoy"]
        fed = macro_snapshot["fed_funds"]
        curve = macro_snapshot["yield_curve_10y_2y"]
        nfci = macro_snapshot["financial_conditions"]
        unemp = macro_snapshot["unemployment"]
        m2_growth = macro_snapshot["m2_growth"]
        fed_trend = macro_snapshot.get("fed_funds_6m_delta", 0.0)

        risk_on = 0
        risk_off = 0
        risk_on += int(cpi < 3.0)
        risk_off += int(cpi > 3.5)
        risk_on += int(curve > 0)
        risk_off += int(curve < -0.4)
        risk_on += int(nfci < 0)
        risk_off += int(nfci > 0.4)
        risk_on += int(m2_growth > 0)
        risk_off += int(m2_growth < -2)
        risk_on += int(unemp < 4.7)
        risk_off += int(unemp > 5.0)

        monetary = "tightening" if fed_trend > 0.15 else ("easing" if fed_trend < -0.15 else "stable")
        spread = risk_on - risk_off

        if spread >= 2:
            regime_label = f"risk_on_{monetary}"
        elif spread <= -2:
            regime_label = f"risk_off_{monetary}"
        else:
            regime_label = f"balanced_{monetary}"

        score = float(np.clip(spread / 5, -1, 1))
        confidence = float(np.clip(0.45 + abs(spread) * 0.12, 0.35, 0.9))

        summary = (
            f"Regime {regime_label} with confidence {confidence:.2f}. Inflation {cpi:.2f}%, Fed Funds {fed:.2f}% "
            f"(6m delta {fed_trend:+.2f}), 10y-2y curve {curve:.2f}%, NFCI {nfci:.2f}, unemployment {unemp:.2f}%, "
            f"M2 growth {m2_growth:.2f}%."
        )
        signal = EngineSignal(score=score, confidence=confidence, summary=summary, evidence=macro_snapshot)
        regime = MarketRegime(
            regime=regime_label,
            score=score,
            confidence=confidence,
            summary=summary,
            evidence=macro_snapshot,
        )
        return regime, signal
