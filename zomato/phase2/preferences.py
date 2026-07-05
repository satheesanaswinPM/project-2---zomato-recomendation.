"""User preference schema, validation, and budget mapping."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from phase1.preprocessor import normalize_city

BudgetLevel = Literal["low", "medium", "high"]

VALID_BUDGETS: tuple[BudgetLevel, ...] = ("low", "medium", "high")
MIN_RATING = 0.0
MAX_RATING = 5.0
MAX_NOTES_LENGTH = 500

BUDGET_RANGES: dict[BudgetLevel, tuple[int, int | float]] = {
    "low": (0, 500),
    "medium": (501, 1500),
    "high": (1501, float("inf")),
}


@dataclass
class UserPreferences:
    location: str
    budget: BudgetLevel
    cuisine: str | None = None
    min_rating: float = 0.0
    additional_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    preferences: UserPreferences | None = None
    errors: dict[str, str] = field(default_factory=dict)
    warnings: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.preferences is not None and not self.errors


def _parse_budget(value: Any) -> tuple[BudgetLevel | None, str | None]:
    if value is None or not str(value).strip():
        return None, "Budget is required (low / medium / high)."

    budget = str(value).strip().lower()
    if budget not in VALID_BUDGETS:
        return None, f"Budget must be one of: {', '.join(VALID_BUDGETS)}."
    return budget, None


def _parse_min_rating(value: Any) -> tuple[float | None, str | None]:
    if value is None or str(value).strip() == "":
        return 0.0, None

    try:
        rating = float(value)
    except (TypeError, ValueError):
        return None, "Minimum rating must be a number between 0 and 5."

    if rating < MIN_RATING or rating > MAX_RATING:
        return None, f"Minimum rating must be between {MIN_RATING} and {MAX_RATING}."

    return round(rating, 1), None


def _parse_cuisine(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_notes(value: Any) -> tuple[str, str | None]:
    if value is None:
        return "", None
    text = str(value).strip()
    if len(text) <= MAX_NOTES_LENGTH:
        return text, None
    return text[:MAX_NOTES_LENGTH], f"Additional notes truncated to {MAX_NOTES_LENGTH} characters."


def parse_preferences(data: dict[str, Any]) -> ValidationResult:
    """Validate raw form/API input and return UserPreferences or field errors."""
    errors: dict[str, str] = {}
    warnings: dict[str, str] = {}

    location_raw = data.get("location")
    if location_raw is None or not str(location_raw).strip():
        errors["location"] = "Location is required."
        location = None
    else:
        location = normalize_city(str(location_raw).strip())
        if not location:
            errors["location"] = "Location is required."

    budget, budget_error = _parse_budget(data.get("budget"))
    if budget_error:
        errors["budget"] = budget_error

    min_rating, rating_error = _parse_min_rating(data.get("min_rating"))
    if rating_error:
        errors["min_rating"] = rating_error

    cuisine = _parse_cuisine(data.get("cuisine"))
    additional_notes, notes_warning = _parse_notes(data.get("additional_notes"))
    if notes_warning:
        warnings["additional_notes"] = notes_warning

    if errors:
        return ValidationResult(errors=errors, warnings=warnings)

    preferences = UserPreferences(
        location=location,  # type: ignore[arg-type]
        budget=budget,  # type: ignore[arg-type]
        cuisine=cuisine,
        min_rating=min_rating or 0.0,
        additional_notes=additional_notes,
    )
    return ValidationResult(preferences=preferences, warnings=warnings)
