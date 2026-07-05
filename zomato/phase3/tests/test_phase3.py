import json
import unittest
from pathlib import Path

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.filter import FilterConfig, filter_restaurants
from phase3.formatter import format_candidates, format_candidates_json
from phase3.pipeline import build_integration
from phase3.prompts import PROMPT_VERSION, build_prompt

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"


class TestFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = build_store(source_path=FIXTURE_PATH)

    def test_filter_by_city_and_budget(self):
        prefs = UserPreferences(location="Bangalore", budget="medium")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        self.assertGreaterEqual(len(result.candidates), 3)
        self.assertTrue(all(r.location == "Bangalore" for r in result.candidates))

    def test_filter_by_budget_medium(self):
        prefs = UserPreferences(location="Bangalore", budget="medium")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        names = {r.name for r in result.candidates}
        self.assertIn("Onesta", names)
        self.assertIn("Jalsa", names)

    def test_filter_by_budget_low(self):
        prefs = UserPreferences(location="Bangalore", budget="low")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        names = {r.name for r in result.candidates}
        self.assertIn("New Restaurant", names)
        self.assertNotIn("Jalsa", names)

    def test_filter_by_cuisine(self):
        prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        names = {r.name for r in result.candidates}
        self.assertEqual(names, {"Onesta"})

    def test_filter_by_cuisine_low_budget(self):
        prefs = UserPreferences(location="Bangalore", budget="low", cuisine="Italian")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        names = {r.name for r in result.candidates}
        self.assertEqual(names, {"New Restaurant"})

    def test_filter_by_min_rating(self):
        prefs = UserPreferences(location="Bangalore", budget="medium", min_rating=4.5)
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        names = {r.name for r in result.candidates}
        self.assertEqual(names, {"Onesta"})

    def test_zero_results_unknown_city(self):
        prefs = UserPreferences(location="Shimla", budget="low")
        result = filter_restaurants(self.store, prefs)
        self.assertTrue(result.is_empty)
        self.assertIn("No restaurants found", result.message or "")

    def test_relax_filters_when_no_exact_match(self):
        prefs = UserPreferences(
            location="Bangalore",
            budget="low",
            cuisine="Italian",
            min_rating=4.5,
        )
        result = filter_restaurants(self.store, prefs)
        self.assertGreater(len(result.candidates), 0)
        self.assertTrue(result.relaxed_filters)
        self.assertIn("minimum rating", result.relaxed_filters)

    def test_impossible_filters_with_relaxation_disabled(self):
        prefs = UserPreferences(
            location="Bangalore",
            budget="low",
            cuisine="Mexican",
            min_rating=5.0,
        )
        result = filter_restaurants(
            self.store, prefs, FilterConfig(relax_on_empty=False)
        )
        self.assertTrue(result.is_empty)

    def test_sorted_by_rating_desc(self):
        prefs = UserPreferences(location="Bangalore", budget="medium")
        result = filter_restaurants(self.store, prefs, FilterConfig(relax_on_empty=False))
        ratings = [r.rating for r in result.candidates if r.rating is not None]
        self.assertEqual(ratings, sorted(ratings, reverse=True))


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.candidates = self.store.get_by_city("Bangalore")[:2]

    def test_format_candidates_compact(self):
        formatted = format_candidates(self.candidates)
        self.assertEqual(len(formatted), 2)
        self.assertIn("name", formatted[0])
        self.assertIn("cuisine", formatted[0])
        self.assertNotIn("locality", formatted[0])

    def test_format_candidates_json_valid(self):
        payload = format_candidates_json(self.candidates)
        parsed = json.loads(payload)
        self.assertIsInstance(parsed, list)


class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.prefs = UserPreferences(
            location="Bangalore",
            budget="medium",
            cuisine="Italian",
            min_rating=4.0,
            additional_notes="family-friendly",
        )
        self.candidates = self.store.get_by_city("Bangalore")

    def test_build_prompt_contains_preferences_and_candidates(self):
        prompt = build_prompt(self.prefs, self.candidates)
        self.assertEqual(prompt.version, PROMPT_VERSION)
        self.assertIn("Do not invent", prompt.system)
        self.assertIn("Bangalore", prompt.user)
        self.assertIn("family-friendly", prompt.user)
        self.assertIn("Onesta", prompt.user)
        self.assertIn("Return JSON", prompt.user)
        self.assertEqual(len(prompt.candidate_names), len(self.candidates))

    def test_build_prompt_candidate_names_grounded(self):
        prompt = build_prompt(self.prefs, self.candidates)
        for name in prompt.candidate_names:
            self.assertTrue(any(r.name == name for r in self.candidates))


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)
        self.prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian")

    def test_build_integration_success(self):
        result = build_integration(self.store, self.prefs)
        self.assertTrue(result.has_prompt)
        assert result.prompt is not None
        self.assertGreater(len(result.candidates_formatted), 0)
        self.assertGreater(len(result.prompt.candidate_names), 0)

    def test_build_integration_empty_city(self):
        prefs = UserPreferences(location="Shimla", budget="low")
        result = build_integration(self.store, prefs)
        self.assertFalse(result.has_prompt)
        self.assertIsNone(result.prompt)
        self.assertTrue(result.filter_result.is_empty)


if __name__ == "__main__":
    unittest.main()
