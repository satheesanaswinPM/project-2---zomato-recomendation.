"""Display-ready models for Phase 5 output."""

from __future__ import annotations

from dataclasses import dataclass, field

from phase4.models import RecommendationResponse


@dataclass
class DisplayRecommendation:
    rank: int
    name: str
    location: str
    cuisine: str
    cost_label: str
    rating_label: str
    explanation: str
    source: str

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "name": self.name,
            "location": self.location,
            "cuisine": self.cuisine,
            "cost_label": self.cost_label,
            "rating_label": self.rating_label,
            "explanation": self.explanation,
            "source": self.source,
        }


@dataclass
class DisplayPayload:
    recommendations: list[DisplayRecommendation] = field(default_factory=list)
    summary: str | None = None
    title: str = "Your Recommendations"
    message: str | None = None
    warnings: list[str] = field(default_factory=list)
    source: str = "llm"
    is_empty: bool = False
    is_error: bool = False

    @classmethod
    def from_response(cls, response: RecommendationResponse) -> "DisplayPayload":
        from phase5.parser import parse_response

        return parse_response(response)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "summary": self.summary,
            "message": self.message,
            "warnings": self.warnings,
            "source": self.source,
            "is_empty": self.is_empty,
            "is_error": self.is_error,
            "recommendations": [item.to_dict() for item in self.recommendations],
        }
