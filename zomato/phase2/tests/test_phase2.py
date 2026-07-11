import json
import unittest

from phase2.app import create_app
from phase2.preferences import BUDGET_RANGES, parse_preferences


class TestPreferences(unittest.TestCase):
    def test_valid_preferences(self):
        result = parse_preferences(
            {
                "location": " Bangalore ",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": "4.0",
                "additional_notes": "Family friendly",
            }
        )
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.location, "Bangalore")
        self.assertEqual(result.preferences.budget, "medium")
        self.assertEqual(result.preferences.cuisine, "Italian")
        self.assertEqual(result.preferences.min_rating, 4.0)

    def test_city_alias_bengaluru(self):
        result = parse_preferences({"location": "bengaluru", "budget": "low"})
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.location, "Bangalore")

    def test_missing_location(self):
        result = parse_preferences({"location": "", "budget": "low"})
        self.assertFalse(result.is_valid)
        self.assertIn("location", result.errors)

    def test_whitespace_only_location(self):
        result = parse_preferences({"location": "   ", "budget": "low"})
        self.assertFalse(result.is_valid)
        self.assertIn("location", result.errors)

    def test_missing_budget(self):
        result = parse_preferences({"location": "Delhi", "budget": ""})
        self.assertFalse(result.is_valid)
        self.assertIn("budget", result.errors)

    def test_invalid_budget(self):
        result = parse_preferences({"location": "Delhi", "budget": "cheap"})
        self.assertFalse(result.is_valid)
        self.assertIn("budget", result.errors)

    def test_custom_budget(self):
        result = parse_preferences(
            {"location": "Bangalore", "budget": "custom", "max_budget": 2000}
        )
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.budget, "custom")
        self.assertEqual(result.preferences.max_budget, 2000)

    def test_custom_budget_missing_amount(self):
        result = parse_preferences({"location": "Bangalore", "budget": "custom"})
        self.assertFalse(result.is_valid)
        self.assertIn("budget", result.errors)

    def test_min_rating_defaults_to_zero(self):
        result = parse_preferences({"location": "Mumbai", "budget": "high"})
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.min_rating, 0.0)

    def test_min_rating_out_of_range(self):
        result = parse_preferences(
            {"location": "Mumbai", "budget": "high", "min_rating": "6"}
        )
        self.assertFalse(result.is_valid)
        self.assertIn("min_rating", result.errors)

    def test_min_rating_rounded(self):
        result = parse_preferences(
            {"location": "Mumbai", "budget": "high", "min_rating": "4.15"}
        )
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.min_rating, 4.2)

    def test_empty_cuisine_becomes_none(self):
        result = parse_preferences({"location": "Delhi", "budget": "low", "cuisine": ""})
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertIsNone(result.preferences.cuisine)

    def test_long_notes_truncated_with_warning(self):
        result = parse_preferences(
            {
                "location": "Delhi",
                "budget": "low",
                "additional_notes": "x" * 600,
            }
        )
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(len(result.preferences.additional_notes), 500)
        self.assertIn("additional_notes", result.warnings)

    def test_unknown_city_still_accepted(self):
        result = parse_preferences({"location": "Shimla", "budget": "medium"})
        self.assertTrue(result.is_valid)
        assert result.preferences is not None
        self.assertEqual(result.preferences.location, "Shimla")

    def test_budget_ranges_defined(self):
        self.assertEqual(BUDGET_RANGES["low"], (0, 500))
        self.assertEqual(BUDGET_RANGES["medium"], (501, 1500))
        self.assertEqual(BUDGET_RANGES["high"][0], 1501)


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Restaurant Preferences", response.data)

    def test_form_submit_success(self):
        response = self.client.post(
            "/submit",
            data={
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "North Indian",
                "min_rating": "4",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Preferences saved", response.data)
        self.assertIn(b"Bangalore", response.data)

    def test_form_submit_validation_error(self):
        response = self.client.post(
            "/submit",
            data={"location": "", "budget": "invalid"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Location is required", response.data)
        self.assertIn(b"Budget must be one of", response.data)

    def test_api_preferences_success(self):
        response = self.client.post(
            "/api/preferences",
            json={"location": "Delhi", "budget": "high", "min_rating": 4.5},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["preferences"]["location"], "Delhi")

    def test_api_preferences_validation_error(self):
        response = self.client.post(
            "/api/preferences",
            json={"location": "Delhi", "budget": "premium"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.data)
        self.assertFalse(payload["ok"])
        self.assertIn("budget", payload["errors"])


if __name__ == "__main__":
    unittest.main()
