from dataclasses import dataclass


@dataclass(frozen=True)
class Restaurant:
    name: str
    location: str
    cuisine: list[str]
    cost_for_two: float | None
    rating: float | None
    votes: int
    restaurant_type: str | None = None
    locality: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "location": self.location,
            "cuisine": self.cuisine,
            "cost_for_two": self.cost_for_two,
            "rating": self.rating,
            "votes": self.votes,
            "restaurant_type": self.restaurant_type,
            "locality": self.locality,
        }
