import json
import unittest

from phase2.preferences import UserPreferences
from phase8.cache import SearchCache, cache_key_for_prefs
from phase8.nl_parser import parse_natural_language
from phase8.refinement import refine_preferences
from phase8.session import SessionStore


class _MockClient:
    def __init__(self, payload: dict):
        self.payload = payload

    def complete(self, system: str, user: str) -> str:
        return json.dumps(self.payload)


class TestNLParser(unittest.TestCase):
    def test_empty_query(self):
        result = parse_natural_language("", client=_MockClient({}))
        self.assertFalse(result.ok)
        self.assertIn("query", result.errors or {})

    def test_parse_success(self):
        client = _MockClient(
            {
                "location": "Marathahalli",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4,
                "additional_notes": "",
            }
        )
        result = parse_natural_language("Italian in Marathahalli", client=client)
        self.assertTrue(result.ok)
        assert result.preferences is not None
        self.assertEqual(result.preferences.location, "Marathahalli")
        self.assertEqual(result.preferences.budget, "medium")


class TestRefinement(unittest.TestCase):
    def test_cheaper_heuristic(self):
        current = UserPreferences(location="HSR", budget="high")
        result = refine_preferences(current, "Show me cheaper options", client=None)
        self.assertTrue(result.ok)
        assert result.preferences is not None
        self.assertEqual(result.preferences.budget, "medium")

    def test_outdoor_notes(self):
        current = UserPreferences(location="HSR", budget="medium")
        result = refine_preferences(current, "Only outdoor seating", client=None)
        self.assertTrue(result.ok)
        assert result.preferences is not None
        self.assertIn("outdoor seating", result.preferences.additional_notes)


class TestCacheAndSession(unittest.TestCase):
    def test_cache_roundtrip(self):
        cache = SearchCache(history_path=None)
        key = cache_key_for_prefs({"location": "BTM", "budget": "low"})
        cache.put(
            key,
            display={"title": "Your Recommendations", "recommendations": []},
            preferences={"location": "BTM", "budget": "low"},
        )
        self.assertIsNotNone(cache.get(key))
        self.assertEqual(len(cache.history()), 1)

    def test_session_create_update(self):
        store = SessionStore()
        prefs = UserPreferences(location="Whitefield", budget="medium")
        state = store.create(prefs, query_label="first")
        updated = store.update(state.session_id, follow_up="cheaper")
        assert updated is not None
        self.assertEqual(updated.history[-1], "cheaper")


if __name__ == "__main__":
    unittest.main()
