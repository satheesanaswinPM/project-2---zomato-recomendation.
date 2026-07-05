"""Data models for Phase 4 recommendation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SourceType = Literal["llm", "fallback"]


@dataclass
class RecommendationResult:
    rank: int
    name: str
    location: str
    cuisine: str
    cost_for_two: float | None
    rating: float | None
    explanation: str
    source: SourceType = "llm"

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "name": self.name,
            "location": self.location,
            "cuisine": self.cuisine,
            "cost_for_two": self.cost_for_two,
            "rating": self.rating,
            "explanation": self.explanation,
            "source": self.source,
        }


@dataclass
class RecommendationResponse:
    recommendations: list[RecommendationResult] = field(default_factory=list)
    summary: str | None = None
    source: SourceType = "llm"
    message: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.recommendations) == 0

    def to_dict(self) -> dict:
        return {
            "recommendations": [item.to_dict() for item in self.recommendations],
            "summary": self.summary,
            "source": self.source,
            "message": self.message,
            "warnings": self.warnings,
        }
