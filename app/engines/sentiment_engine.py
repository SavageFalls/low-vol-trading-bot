from __future__ import annotations

import re
from typing import List, Dict

import numpy as np

POSITIVE = {
    "beat", "surge", "upgrade", "growth", "strong", "record", "optimistic", "outperform", "bullish", "expands"
}
NEGATIVE = {
    "miss", "downgrade", "weak", "lawsuit", "decline", "cuts", "recession", "bearish", "risk", "fraud"
}


class SentimentEngine:
    def analyze(self, news_items: List[Dict]) -> dict:
        if not news_items:
            return {"score": 0.0, "summary": "No recent headlines."}

        scores = []
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            tokens = re.findall(r"[a-z]+", text)
            pos = sum(1 for t in tokens if t in POSITIVE)
            neg = sum(1 for t in tokens if t in NEGATIVE)
            raw = (pos - neg) / max(1, pos + neg)
            scores.append(raw)

        base = float(np.mean(scores))
        # contrarian adjustment: excessive positivity lowers forward edge.
        if base > 0.45:
            adjusted = base - 0.2
            summary = "Sentiment euphoric; contrarian caution."
        elif base < -0.35:
            adjusted = base + 0.25
            summary = "Sentiment pessimistic; contrarian upside possible."
        else:
            adjusted = base
            summary = "Sentiment balanced."

        return {"score": float(np.clip(adjusted, -1, 1)), "summary": summary}
