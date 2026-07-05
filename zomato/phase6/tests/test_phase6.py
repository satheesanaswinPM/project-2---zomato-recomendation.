import json
import unittest
from unittest.mock import patch

from phase4.models import RecommendationResponse, RecommendationResult
from phase6.app import create_app
from phase6.orchestrator import run_recommendation_search
from phase6.schemas import ErrorResponse, HealthResponse, SuccessResponse

FIXTURE = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "phase1"
    / "tests"
    / "fixtures"
    / "sample_zomato.csv"
)

MOCK_RESPONSE = RecommendationResponse(
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


class TestSchemas(unittest.TestCase):
    def test_health_response(self):
        self.assertEqual(HealthResponse().to_dict(), {"status": "ok"})

    def test_error_response(self):
        payload = ErrorResponse(errors={"location": "Location is required."})
        self.assertFalse(payload.to_dict()["ok"])
        self.assertIn("location", payload.to_dict()["errors"])

    def test_success_response(self):
        payload = SuccessResponse(display={"title": "Your Recommendations"})
        data = payload.to_dict()
        self.assertTrue(data["ok"])
        self.assertEqual(data["display"]["title"], "Your Recommendations")


class TestOrchestrator(unittest.TestCase):
    def test_validation_error(self):
        result = run_recommendation_search({"location": "", "budget": "low"})
        self.assertFalse(result.ok)
        self.assertEqual(result.status_code, 400)
        self.assertIn("location", result.errors)

    def test_success_with_mock(self):
        with patch(
            "phase6.orchestrator.build_recommendations", return_value=MOCK_RESPONSE
        ):
            result = run_recommendation_search(
                {"location": "Bangalore", "budget": "medium"},
                source_path=FIXTURE,
            )
        self.assertTrue(result.ok)
        assert result.display is not None
        self.assertEqual(result.display.recommendations[0].name, "Onesta")

    def test_pipeline_exception_returns_error_display(self):
        with patch(
            "phase6.orchestrator.build_integration",
            side_effect=RuntimeError("store unavailable"),
        ):
            result = run_recommendation_search(
                {"location": "Bangalore", "budget": "medium"},
                source_path=FIXTURE,
            )
        self.assertTrue(result.ok)
        assert result.display is not None
        self.assertTrue(result.display.is_error)


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_cors_headers(self):
        response = self.client.get("/api/health")
        self.assertIn("Access-Control-Allow-Origin", response.headers)

    def test_recommendations_success(self):
        with patch(
            "phase6.orchestrator.build_recommendations", return_value=MOCK_RESPONSE
        ):
            response = self.client.post(
                "/api/recommendations",
                json={"location": "Bangalore", "budget": "medium"},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["display"]["recommendations"][0]["name"], "Onesta")

    def test_recommendations_validation_error(self):
        response = self.client.post(
            "/api/recommendations",
            json={"location": "", "budget": "high"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.data)
        self.assertFalse(payload["ok"])
        self.assertIn("location", payload["errors"])

    def test_options_preflight(self):
        response = self.client.options("/api/recommendations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Access-Control-Allow-Methods", response.headers)


if __name__ == "__main__":
    unittest.main()
