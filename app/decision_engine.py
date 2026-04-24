from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class DecisionOutput:
    score: float
    confidence: float
    rating: str
    rationale: str


class DecisionEngine:
    # Top-down precedence: macro -> positioning -> sentiment -> fundamentals -> technical.
    BASE_WEIGHTS = {
        "macro": 0.30,
        "positioning": 0.20,
        "sentiment": 0.15,
        "fundamental": 0.15,
        "technical": 0.20,
    }

    def evaluate(self, signals: Dict[str, Dict]) -> DecisionOutput:
        w = self.BASE_WEIGHTS.copy()
        macro_score = signals["macro"]["score"]

        # Dynamic weighting by regime
        if macro_score < -0.2:
            w["technical"] -= 0.05
            w["macro"] += 0.05
        elif macro_score > 0.25:
            w["technical"] += 0.05
            w["sentiment"] -= 0.05

        weighted = (
            w["macro"] * signals["macro"]["score"]
            + w["positioning"] * signals["positioning"]["score"]
            + w["sentiment"] * signals["sentiment"]["score"]
            + w["fundamental"] * signals["fundamental"]["score"]
            + w["technical"] * signals["technical"]["score"]
        )

        # conflict penalty (macro vs technical, sentiment vs positioning)
        conflict_penalty = 0.0
        if signals["macro"]["score"] * signals["technical"]["score"] < 0:
            conflict_penalty += 0.08
        if signals["sentiment"]["score"] * signals["positioning"]["score"] < 0:
            conflict_penalty += 0.05

        score = float(np.clip(weighted - conflict_penalty, -1, 1))
        confidence = float(min(0.97, max(0.35, abs(score) + 0.25 - conflict_penalty / 2)))
        rating = self._rating(score, confidence)
        rationale = self._build_rationale(signals, conflict_penalty)
        return DecisionOutput(score=score, confidence=confidence, rating=rating, rationale=rationale)

    def _rating(self, score: float, confidence: float) -> str:
        # stringent criteria to avoid overusing Major ratings.
        if score >= 0.62 and confidence >= 0.82:
            return "Major Buy"
        if score >= 0.22:
            return "Buy"
        if score <= -0.62 and confidence >= 0.82:
            return "Major Sell"
        if score <= -0.22:
            return "Sell"
        return "Hold"

    def _build_rationale(self, signals: Dict[str, Dict], conflict_penalty: float) -> str:
        parts = [
            f"Macro={signals['macro']['score']:.2f}",
            f"Positioning={signals['positioning']['score']:.2f}",
            f"Sentiment={signals['sentiment']['score']:.2f}",
            f"Fundamental={signals['fundamental']['score']:.2f}",
            f"Technical={signals['technical']['score']:.2f}",
        ]
        if conflict_penalty > 0:
            parts.append(f"Conflict penalty={conflict_penalty:.2f}")
        return " | ".join(parts)
