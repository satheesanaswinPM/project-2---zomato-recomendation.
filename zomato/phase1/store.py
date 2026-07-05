"""In-memory restaurant store with city-based queries."""

from __future__ import annotations

from phase1.models import Restaurant
from phase1.preprocessor import normalize_city


class RestaurantStore:
    def __init__(self, restaurants: list[Restaurant]):
        self._restaurants = list(restaurants)
        self._by_city: dict[str, list[Restaurant]] = {}
        for restaurant in self._restaurants:
            city_key = restaurant.location.lower()
            self._by_city.setdefault(city_key, []).append(restaurant)

    @property
    def count(self) -> int:
        return len(self._restaurants)

    def cities(self) -> list[str]:
        return sorted({r.location for r in self._restaurants})

    def get_by_city(self, city: str) -> list[Restaurant]:
        """Return all restaurants in the given city (case-insensitive, alias-aware)."""
        normalized = normalize_city(city)
        if not normalized:
            return []
        return list(self._by_city.get(normalized.lower(), []))

    def sample(self, n: int = 5) -> list[Restaurant]:
        return self._restaurants[:n]

    def validation_report(self) -> dict:
        missing_rating = sum(1 for r in self._restaurants if r.rating is None)
        missing_cost = sum(1 for r in self._restaurants if r.cost_for_two is None)
        return {
            "total_restaurants": self.count,
            "cities": self.cities(),
            "city_count": len(self.cities()),
            "missing_rating": missing_rating,
            "missing_cost": missing_cost,
        }
