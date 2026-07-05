import json
import unittest
from unittest.mock import patch

from phase4.models import RecommendationResponse, RecommendationResult
from phase5.app import create_app
from phase5.parser import parse_response
from phase5.pipeline import build_display_payload, present
from phase5.renderer import render_html, render_json, render_text


class TestParser(unittest.TestCase):
    def test_parse_full_response(self):
        response = RecommendationResponse(
            recommendations=[
                RecommendationResult(
                    rank=1,
                    name="Spice Garden",
                    location="Bangalore",
                    cuisine="North Indian",
                    cost_for_two=800.0,
                    rating=4.5,
                    explanation="Great match for your budget.",
                )
            ],
            summary="Top pick: Spice Garden.",
            source="llm",
        )
        payload = parse_response(response)
        self.assertEqual(len(payload.recommendations), 1)
        self.assertEqual(payload.recommendations[0].cost_label, "Rs.800")
        self.assertEqual(payload.recommendations[0].rating_label, "4.5")
        self.assertEqual(payload.summary, "Top pick: Spice Garden.")

    def test_parse_missing_cost_and_rating(self):
        response = RecommendationResponse(
            recommendations=[
                RecommendationResult(
                    rank=1,
                    name="New Place",
                    location="Bangalore",
                    cuisine="",
                    cost_for_two=None,
                    rating=None,
                    explanation="",
                )
            ],
        )
        payload = parse_response(response)
        self.assertEqual(payload.recommendations[0].cost_label, "Price not available")
        self.assertEqual(payload.recommendations[0].rating_label, "Unrated")
        self.assertEqual(payload.recommendations[0].cuisine, "Cuisine not listed")
        self.assertIn("Recommended based on", payload.recommendations[0].explanation)

    def test_empty_state(self):
        payload = parse_response(RecommendationResponse(message="No matches."))
        self.assertTrue(payload.is_empty)
        self.assertTrue(payload.is_error)

    def test_fallback_notice(self):
        response = RecommendationResponse(
            recommendations=[
                RecommendationResult(
                    rank=1,
                    name="A",
                    location="Bangalore",
                    cuisine="Indian",
                    cost_for_two=500,
                    rating=4.0,
                    explanation="Template.",
                    source="fallback",
                )
            ],
            source="fallback",
        )
        payload = parse_response(response)
        self.assertIn("AI explanations unavailable", payload.message or "")


class TestRenderer(unittest.TestCase):
    def setUp(self):
        self.payload = parse_response(
            RecommendationResponse(
                recommendations=[
                    RecommendationResult(
                        rank=1,
                        name="Onesta",
                        location="Bangalore",
                        cuisine="Italian",
                        cost_for_two=600,
                        rating=4.6,
                        explanation="Best Italian pick.",
                    )
                ],
                summary="Top recommendations for you: Onesta.",
            )
        )

    def test_render_text(self):
        text = render_text(self.payload)
        self.assertIn("#1  Onesta", text)
        self.assertIn("Why: Best Italian pick.", text)
        self.assertIn("Top recommendations", text)

    def test_render_html_cards(self):
        html = render_html(self.payload)
        self.assertIn('class="result-card"', html)
        self.assertIn("Onesta", html)
        self.assertIn("Why:", html)

    def test_render_json(self):
        data = json.loads(render_json(self.payload))
        self.assertEqual(data["recommendations"][0]["name"], "Onesta")

    def test_render_empty_state(self):
        empty = parse_response(RecommendationResponse(message="No restaurants found."))
        html = render_html(empty)
        self.assertIn("empty-state", html)


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_index_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Restaurant Finder", response.data)

    def test_search_validation_error(self):
        response = self.client.post("/search", data={"location": "", "budget": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Location is required", response.data)

    def test_api_search_returns_display(self):
        mock_response = RecommendationResponse(
            recommendations=[
                RecommendationResult(
                    rank=1,
                    name="Onesta",
                    location="Bangalore",
                    cuisine="Italian",
                    cost_for_two=600,
                    rating=4.6,
                    explanation="Best pick.",
                )
            ],
            summary="Top recommendations for you: Onesta.",
        )
        with patch("phase5.app.build_recommendations", return_value=mock_response):
            response = self.client.post(
                "/api/search",
                json={"location": "Bangalore", "budget": "medium"},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["display"]["recommendations"][0]["name"], "Onesta")


if __name__ == "__main__":
    unittest.main()
