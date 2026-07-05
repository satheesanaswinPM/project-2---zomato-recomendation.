import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.pipeline import build_integration
from phase4.fallback import build_fallback_recommendations
from phase4.guard import guard_recommendations
from phase4.llm_client import GroqClient
from phase4.models import RecommendationResult
from phase4.parser import ParseError, parse_recommendations
from phase4.pipeline import build_recommendations
from phase4.recommender import recommend

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"

VALID_LLM_JSON = json.dumps(
    [
        {
            "rank": 1,
            "name": "Onesta",
            "explanation": "Great Italian options within medium budget.",
        },
        {
            "rank": 2,
            "name": "Jalsa",
            "explanation": "Solid North Indian choice with good ratings.",
        },
    ]
)

HALLUCINATED_LLM_JSON = json.dumps(
    [
        {"rank": 1, "name": "Onesta", "explanation": "Valid pick."},
        {"rank": 2, "name": "The Golden Fork", "explanation": "Fake restaurant."},
    ]
)


class FakeGroqClient:
    def __init__(self, responses: list[str]):
        self.responses = list(responses)
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        if self.calls - 1 < len(self.responses):
            return self.responses[self.calls - 1]
        return self.responses[-1]


class TestParser(unittest.TestCase):
    def test_parse_json_array(self):
        items = parse_recommendations(VALID_LLM_JSON)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["name"], "Onesta")

    def test_parse_json_in_markdown_fence(self):
        text = f"```json\n{VALID_LLM_JSON}\n```"
        items = parse_recommendations(text)
        self.assertEqual(items[0]["name"], "Onesta")

    def test_parse_wrapped_object(self):
        text = json.dumps({"recommendations": json.loads(VALID_LLM_JSON)})
        items = parse_recommendations(text)
        self.assertEqual(len(items), 2)

    def test_parse_invalid_json_raises(self):
        with self.assertRaises(ParseError):
            parse_recommendations("not json at all")


class TestGuard(unittest.TestCase):
    def test_removes_hallucinated_restaurant(self):
        items = parse_recommendations(HALLUCINATED_LLM_JSON)
        sanitized, warnings = guard_recommendations(items, ["Onesta", "Jalsa"])
        self.assertEqual(len(sanitized), 1)
        self.assertEqual(sanitized[0]["name"], "Onesta")
        self.assertTrue(warnings)

    def test_fuzzy_match_close_name(self):
        items = [{"rank": 1, "name": "Onest", "explanation": "close"}]
        sanitized, _ = guard_recommendations(items, ["Onesta", "Jalsa"])
        self.assertEqual(sanitized[0]["name"], "Onesta")


class TestFallback(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.prefs = UserPreferences(location="Bangalore", budget="medium")
        self.candidates = self.store.get_by_city("Bangalore")

    def test_fallback_sorted_by_rating(self):
        response = build_fallback_recommendations(self.candidates, self.prefs, top_n=3)
        self.assertEqual(response.source, "fallback")
        self.assertGreater(len(response.recommendations), 0)
        self.assertEqual(response.recommendations[0].name, "Onesta")


class TestRecommender(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.prefs = UserPreferences(
            location="Bangalore",
            budget="medium",
            cuisine="Italian",
            min_rating=4.0,
        )
        self.integration = build_integration(self.store, self.prefs)

    def test_recommend_with_mock_groq(self):
        assert self.integration.prompt is not None
        client = FakeGroqClient([VALID_LLM_JSON])
        response = recommend(
            self.integration.prompt,
            self.integration.filter_result.candidates,
            self.prefs,
            client=client,
        )
        self.assertEqual(response.source, "llm")
        self.assertGreaterEqual(len(response.recommendations), 1)
        self.assertEqual(response.recommendations[0].name, "Onesta")
        self.assertIsNotNone(response.recommendations[0].rating)

    def test_recommend_strips_hallucinations(self):
        assert self.integration.prompt is not None
        client = FakeGroqClient([HALLUCINATED_LLM_JSON])
        response = recommend(
            self.integration.prompt,
            self.integration.filter_result.candidates,
            self.prefs,
            client=client,
        )
        names = {item.name for item in response.recommendations}
        self.assertNotIn("The Golden Fork", names)
        self.assertTrue(response.warnings)

    def test_recommend_fallback_on_api_error(self):
        assert self.integration.prompt is not None

        class FailingClient:
            def complete(self, system: str, user: str) -> str:
                raise RuntimeError("API down")

        response = recommend(
            self.integration.prompt,
            self.integration.filter_result.candidates,
            self.prefs,
            client=FailingClient(),
        )
        self.assertEqual(response.source, "fallback")
        self.assertGreater(len(response.recommendations), 0)

    def test_recommend_fallback_on_bad_json(self):
        assert self.integration.prompt is not None
        client = FakeGroqClient(["invalid response", "still invalid"])
        response = recommend(
            self.integration.prompt,
            self.integration.filter_result.candidates,
            self.prefs,
            client=client,
        )
        self.assertEqual(response.source, "fallback")
        self.assertEqual(client.calls, 2)

    def test_empty_candidates_returns_message(self):
        assert self.integration.prompt is not None
        response = recommend(
            self.integration.prompt,
            [],
            self.prefs,
            client=FakeGroqClient([VALID_LLM_JSON]),
        )
        self.assertTrue(response.is_empty)
        self.assertIn("No candidates", response.message or "")


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
        self.integration = build_integration(self.store, self.prefs)

    def test_build_recommendations_end_to_end(self):
        client = FakeGroqClient([VALID_LLM_JSON])
        response = build_recommendations(
            self.integration,
            self.prefs,
            client=client,
        )
        self.assertFalse(response.is_empty)
        first = response.recommendations[0]
        self.assertIsInstance(first, RecommendationResult)
        self.assertTrue(first.cuisine)
        self.assertIsNotNone(first.explanation)


class TestGroqClientConfig(unittest.TestCase):
    def test_missing_api_key_raises(self):
        client = GroqClient()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                client.complete("system", "user")


if __name__ == "__main__":
    unittest.main()
