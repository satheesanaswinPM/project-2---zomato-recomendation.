"""Data models for the Phase 3 integration layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from phase1.models import Restaurant


@dataclass
class FilterResult:
    candidates: list[Restaurant]
    relaxed_filters: list[str] = field(default_factory=list)
    message: str | None = None

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0


@dataclass
class PromptBundle:
    version: str
    system: str
    user: str
    candidate_names: list[str]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "system": self.system,
            "user": self.user,
            "candidate_names": self.candidate_names,
        }


@dataclass
class IntegrationResult:
    filter_result: FilterResult
    prompt: PromptBundle | None
    candidates_formatted: list[dict]

    @property
    def has_prompt(self) -> bool:
        return self.prompt is not None and not self.filter_result.is_empty
