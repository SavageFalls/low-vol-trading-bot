from __future__ import annotations

from app.models import EngineSignal


class DecisionEngine:
    WEIGHTS = {
        "macro": 0.30,
        "positioning": 0.25,
        "sentiment": 0.20,
        "fundamental": 0.15,
        "technical": 0.10,
    }

    @staticmethod
    def _missing_penalty(signals: dict[str, EngineSignal]) -> float:
        penalty = 0.0
        for sig in signals.values():
            if sig.confidence < 0.35:
                penalty += 0.12
            elif sig.confidence < 0.5:
                penalty += 0.06
        return penalty

    def score(
        self,
        macro: EngineSignal,
        positioning: EngineSignal,
        sentiment: EngineSignal,
        fundamental: EngineSignal,
        technical: EngineSignal,
    ) -> tuple[float, float, str]:
        signals = {
            "macro": macro,
            "positioning": positioning,
            "sentiment": sentiment,
            "fundamental": fundamental,
            "technical": technical,
        }
        weighted = {k: self.WEIGHTS[k] * signals[k].score for k in signals}
        raw_composite = sum(weighted.values())
        confidence = sum(self.WEIGHTS[k] * signals[k].confidence for k in signals)
        penalty = self._missing_penalty(signals)

        positives = sum(1 for s in signals.values() if s.score > 0.25)
        negatives = sum(1 for s in signals.values() if s.score < -0.25)
        conflict_penalty = 0.08 if positives >= 2 and negatives >= 2 else 0.0

        composite = raw_composite - penalty - conflict_penalty

        trace = (
            f"macro={weighted['macro']:+.3f}, flows={weighted['positioning']:+.3f}, sentiment={weighted['sentiment']:+.3f}, "
            f"fundamentals={weighted['fundamental']:+.3f}, technicals={weighted['technical']:+.3f}, "
            f"missing_penalty={penalty:.3f}, conflict_penalty={conflict_penalty:.3f}, total={composite:+.3f}"
        )
        return composite, confidence, trace

    def rating(self, composite: float, confidence: float) -> str:
        # Force neutrality unless edge is strong.
        if composite >= 0.62 and confidence >= 0.76:
            return "Major Buy"
        if composite >= 0.38 and confidence >= 0.66:
            return "Buy"
        if composite <= -0.62 and confidence >= 0.76:
            return "Major Sell"
        if composite <= -0.38 and confidence >= 0.66:
            return "Sell"
        return "Hold"
