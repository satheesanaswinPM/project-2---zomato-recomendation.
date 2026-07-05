"""Filter restaurants by user preferences with optional filter relaxation."""

from __future__ import annotations

from dataclasses import dataclass

from phase1.models import Restaurant
from phase1.store import RestaurantStore
from phase2.preferences import BUDGET_RANGES, UserPreferences
from phase3.models import FilterResult


@dataclass
class FilterConfig:
    max_candidates: int = 20
    relax_on_empty: bool = True


def _matches_budget(restaurant: Restaurant, budget: str) -> bool:
    if restaurant.cost_for_two is None:
        return False
    low, high = BUDGET_RANGES[budget]  # type: ignore[index]
    cost = restaurant.cost_for_two
    return low <= cost <= high


def _matches_cuisine(restaurant: Restaurant, cuisine: str) -> bool:
    needle = cuisine.strip().lower()
    if not needle:
        return True
    return any(needle in item.lower() for item in restaurant.cuisine)


def _matches_rating(restaurant: Restaurant, min_rating: float) -> bool:
    if min_rating <= 0:
        return True
    if restaurant.rating is None:
        return False
    return restaurant.rating >= min_rating


def _apply_filters(
    restaurants: list[Restaurant],
    preferences: UserPreferences,
    *,
    apply_cuisine: bool,
    apply_rating: bool,
    apply_budget: bool,
) -> list[Restaurant]:
    results = restaurants

    if apply_budget:
        results = [r for r in results if _matches_budget(r, preferences.budget)]

    if apply_cuisine and preferences.cuisine:
        results = [r for r in results if _matches_cuisine(r, preferences.cuisine)]

    if apply_rating and preferences.min_rating > 0:
        results = [r for r in results if _matches_rating(r, preferences.min_rating)]

    return results


def _sort_candidates(restaurants: list[Restaurant]) -> list[Restaurant]:
    return sorted(
        restaurants,
        key=lambda r: (r.rating if r.rating is not None else -1.0, r.votes),
        reverse=True,
    )


def _cap_candidates(restaurants: list[Restaurant], max_candidates: int) -> list[Restaurant]:
    return restaurants[:max_candidates]


def filter_restaurants(
    store: RestaurantStore,
    preferences: UserPreferences,
    config: FilterConfig | None = None,
) -> FilterResult:
    """
    Filter restaurants by location, budget, cuisine, and rating.

    When no matches are found and relax_on_empty is enabled, progressively
    relaxes rating, cuisine, then budget filters.
    """
    config = config or FilterConfig()
    city_restaurants = store.get_by_city(preferences.location)

    if not city_restaurants:
        return FilterResult(
            candidates=[],
            message=(
                f"No restaurants found in {preferences.location}. "
                f"Available cities: {', '.join(store.cities()) or 'none'}."
            ),
        )

    relaxed: list[str] = []
    apply_cuisine = bool(preferences.cuisine)
    apply_rating = preferences.min_rating > 0
    apply_budget = True

    candidates = _apply_filters(
        city_restaurants,
        preferences,
        apply_cuisine=apply_cuisine,
        apply_rating=apply_rating,
        apply_budget=apply_budget,
    )

    if not candidates and config.relax_on_empty:
        if apply_rating:
            apply_rating = False
            relaxed.append("minimum rating")
            candidates = _apply_filters(
                city_restaurants,
                preferences,
                apply_cuisine=apply_cuisine,
                apply_rating=False,
                apply_budget=apply_budget,
            )

        if not candidates and apply_cuisine:
            apply_cuisine = False
            relaxed.append("cuisine")
            candidates = _apply_filters(
                city_restaurants,
                preferences,
                apply_cuisine=False,
                apply_rating=False,
                apply_budget=apply_budget,
            )

        if not candidates and apply_budget:
            apply_budget = False
            relaxed.append("budget")
            candidates = _apply_filters(
                city_restaurants,
                preferences,
                apply_cuisine=False,
                apply_rating=False,
                apply_budget=False,
            )

    candidates = _cap_candidates(_sort_candidates(candidates), config.max_candidates)

    message = None
    if not candidates:
        message = (
            "No restaurants match your preferences. "
            "Try lowering your minimum rating, changing cuisine, or adjusting budget."
        )
    elif relaxed:
        message = (
            "No exact matches found. Showing closest results with relaxed filters: "
            + ", ".join(relaxed)
            + "."
        )

    return FilterResult(candidates=candidates, relaxed_filters=relaxed, message=message)
