from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class EngineSignal:
    score: float
    confidence: float
    summary: str
    evidence: Dict[str, float | str] = field(default_factory=dict)


@dataclass
class Opportunity:
    ticker: str
    rating: str
    confidence: float
    composite_score: float
    macro_view: str
    positioning_flows: str
    sentiment: str
    fundamentals: str
    key_levels: str
    thesis: str
    decision_trace: str
    engine_breakdown: Dict[str, EngineSignal]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["generated_at"] = self.generated_at.isoformat()
        return data


@dataclass
class MarketRegime:
    regime: str
    score: float
    confidence: float
    summary: str
    evidence: Dict[str, float]


@dataclass
class DailyResearchReport:
    created_at: datetime
    benchmark: str
    benchmark_context: str
    macro_regime: str
    macro_confidence: float
    macro_explanation: str
    opportunities: List[Opportunity]

    def to_dict(self) -> Dict:
        return {
            "created_at": self.created_at.isoformat(),
            "benchmark": self.benchmark,
            "benchmark_context": self.benchmark_context,
            "macro_regime": self.macro_regime,
            "macro_confidence": self.macro_confidence,
            "macro_explanation": self.macro_explanation,
            "opportunities": [o.to_dict() for o in self.opportunities],
        }
