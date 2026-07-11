"""Phase 9 validation: Streamlit module structure and store/locality smoke test."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_FILES = [
    "app.py",
    "ui.py",
    "requirements.txt",
    "README.md",
    ".streamlit/config.toml",
    ".streamlit/secrets.toml.example",
]


def check_structure() -> dict:
    base = Path(__file__).resolve().parent
    missing = [name for name in REQUIRED_FILES if not (base / name).exists()]
    return {
        "required_count": len(REQUIRED_FILES),
        "missing": missing,
        "structure_ok": not missing,
    }


def check_pipeline() -> dict:
    from phase6.orchestrator import build_default_store, run_recommendation_search

    fixture = ROOT / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"
    store = build_default_store(source_path=fixture)
    localities = store.localities("Bangalore")

    class _MockClient:
        def complete(self, system: str, user: str) -> str:
            return json.dumps(
                [
                    {
                        "rank": 1,
                        "name": "Onesta",
                        "explanation": "Great Italian pick for the medium budget.",
                    }
                ]
            )

    search = run_recommendation_search(
        {
            "location": "Banashankari",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
        client=_MockClient(),
        store=store,
        source_path=fixture,
    )

    return {
        "locality_count": len(localities),
        "has_banashankari": "Banashankari" in localities,
        "search_ok": search.ok,
        "result_count": len(search.display.recommendations) if search.display else 0,
    }


def run_validation() -> dict:
    report = check_structure()
    if report["structure_ok"]:
        report.update(check_pipeline())
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 9 Streamlit app")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch Streamlit app (streamlit run phase9/app.py)",
    )
    args = parser.parse_args()

    if args.serve:
        import subprocess

        app_path = Path(__file__).resolve().parent / "app.py"
        raise SystemExit(
            subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)])
        )

    report = run_validation()
    if not report.get("structure_ok"):
        raise SystemExit("Phase 9 validation failed: missing files.")
    if not report.get("search_ok"):
        raise SystemExit("Phase 9 validation failed: orchestrator search.")
    logger.info("Phase 9 validation passed.")


if __name__ == "__main__":
    main()
