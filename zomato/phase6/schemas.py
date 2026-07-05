"""API request and response schemas for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthResponse:
    status: str = "ok"

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status}


@dataclass
class ErrorResponse:
    ok: bool = False
    errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "errors": self.errors}


@dataclass
class SuccessResponse:
    ok: bool = True
    display: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "display": self.display}
