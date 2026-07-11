import unittest
from pathlib import Path

from phase1.loader import load_raw_dataset
from phase1.pipeline import build_store
from phase1.preprocessor import (
    extract_city_from_address,
    normalize_city,
    parse_cost,
    parse_cuisines,
    parse_rating,
    preprocess,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_zomato.csv"


class TestPreprocessor(unittest.TestCase):
    def test_normalize_city_aliases(self):
        self.assertEqual(normalize_city("bengaluru"), "Bangalore")
        self.assertEqual(normalize_city("BLR"), "Bangalore")
        self.assertEqual(normalize_city("new delhi"), "Delhi")

    def test_parse_rating(self):
        self.assertEqual(parse_rating("4.1/5"), 4.1)
        self.assertIsNone(parse_rating("new"))
        self.assertIsNone(parse_rating(None))
        self.assertEqual(parse_rating("6.2/5"), 5.0)

    def test_parse_cost(self):
        self.assertEqual(parse_cost("800"), 800.0)
        self.assertEqual(parse_cost("1,200"), 1200.0)
        self.assertIsNone(parse_cost(""))

    def test_parse_cuisines(self):
        self.assertEqual(parse_cuisines("North Indian, Mughlai"), ["North Indian", "Mughlai"])
        self.assertEqual(parse_cuisines(""), ["Unknown"])

    def test_extract_city_from_address(self):
        address = "942, 21st Main Road, Banashankari, Bangalore"
        self.assertEqual(extract_city_from_address(address), "Bangalore")

    def test_preprocess_drops_missing_name(self):
        raw_df = load_raw_dataset(source_path=FIXTURE_PATH)
        restaurants = preprocess(raw_df)
        names = [r.name for r in restaurants]
        self.assertNotIn("", names)
        self.assertEqual(len(restaurants), 6)


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = build_store(source_path=FIXTURE_PATH)

    def test_get_by_city_bangalore(self):
        results = self.store.get_by_city("Bangalore")
        self.assertEqual(len(results), 5)

    def test_get_by_city_alias(self):
        canonical = self.store.get_by_city("Bangalore")
        alias = self.store.get_by_city("Bengaluru")
        self.assertEqual(len(alias), len(canonical))

    def test_get_by_city_delhi(self):
        results = self.store.get_by_city("Delhi")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Delhi Darbar")

    def test_get_by_unknown_city(self):
        self.assertEqual(self.store.get_by_city("Shimla"), [])

    def test_localities_for_bangalore(self):
        localities = self.store.localities("Bangalore")
        self.assertIn("Banashankari", localities)

    def test_get_by_location_locality(self):
        results = self.store.get_by_location("Banashankari")
        self.assertGreater(len(results), 0)
        self.assertTrue(all(r.locality == "Banashankari" for r in results))

    def test_validation_report(self):
        report = self.store.validation_report()
        self.assertEqual(report["total_restaurants"], 6)
        self.assertIn("Bangalore", report["cities"])
        self.assertIn("Delhi", report["cities"])


if __name__ == "__main__":
    unittest.main()
