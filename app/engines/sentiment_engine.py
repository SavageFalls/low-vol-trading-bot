from __future__ import annotations

import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.models import EngineSignal


class SentimentEngine:
    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, news_items: list[dict]) -> EngineSignal:
        if not news_items:
            return EngineSignal(
                score=-0.2,
                confidence=0.25,
                summary="Sentiment unknown: no parsable headlines returned from configured RSS feeds.",
                evidence={"classification": "unknown", "sample": 0},
            )

        ordered = sorted(news_items, key=lambda x: x.get("published", ""))
        scores = []
        for item in ordered[:60]:
            txt = f"{item.get('title', '')}. {item.get('summary', '')}".strip()
            if not txt:
                continue
            scores.append(self.analyzer.polarity_scores(txt)["compound"])

        if not scores:
            return EngineSignal(
                score=-0.2,
                confidence=0.25,
                summary="Sentiment unknown: headlines fetched but text parsing failed.",
                evidence={"classification": "unknown", "sample": 0},
            )

        avg = float(np.mean(scores))
        std = float(np.std(scores)) if len(scores) > 1 else 0.0
        split = max(1, len(scores) // 2)
        first_half = float(np.mean(scores[:split]))
        second_half = float(np.mean(scores[split:]))
        shift = second_half - first_half

        classification = "bullish" if avg > 0.15 else ("bearish" if avg < -0.15 else "neutral")
        adjusted = avg - 0.35 * shift

        confidence = float(np.clip(0.4 + min(len(scores), 40) / 90 - std * 0.2, 0.25, 0.85))
        summary = (
            f"Sentiment={classification}; avg={avg:+.2f}, narrative_shift={shift:+.2f}, dispersion={std:.2f}, "
            f"sample={len(scores)}."
        )
        return EngineSignal(
            score=float(np.clip(adjusted, -1, 1)),
            confidence=confidence,
            summary=summary,
            evidence={
                "classification": classification,
                "avg_sentiment": avg,
                "narrative_shift": shift,
                "dispersion": std,
                "sample": len(scores),
            },
        )
