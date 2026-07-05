"""Phase 7 validation: Next.js frontend structure and optional API check."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_FILES = [
    "package.json",
    "tsconfig.json",
    "next.config.ts",
    "tailwind.config.ts",
    "src/app/layout.tsx",
    "src/app/page.tsx",
    "src/app/globals.css",
    "src/lib/api.ts",
    "src/lib/types.ts",
    "src/components/RestaurantFinder.tsx",
    "src/components/SearchForm.tsx",
    "src/components/RecommendationCard.tsx",
    "src/components/ResultsPanel.tsx",
    "src/components/ResultsSkeleton.tsx",
    "src/components/EmptyState.tsx",
    "src/components/ErrorBanner.tsx",
    ".env.example",
    "README.md",
]


def check_structure() -> dict:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    return {
        "required_count": len(REQUIRED_FILES),
        "missing": missing,
        "structure_ok": not missing,
    }


def check_api(base_url: str) -> dict:
    url = f"{base_url.rstrip('/')}/api/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {
            "api_url": url,
            "api_reachable": True,
            "api_ok": data.get("status") == "ok",
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "api_url": url,
            "api_reachable": False,
            "api_ok": False,
            "error": str(exc),
        }


def run_validation(*, check_api_flag: bool = False, api_base: str = "http://localhost:8000") -> dict:
    report = check_structure()
    if check_api_flag:
        report.update(check_api(api_base))
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 7 Next.js frontend")
    parser.add_argument(
        "--check-api",
        action="store_true",
        help="Verify Phase 6 backend health endpoint is reachable",
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000",
        help="Phase 6 API base URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    report = run_validation(check_api_flag=args.check_api, api_base=args.api_base)

    if not report["structure_ok"]:
        raise SystemExit("Phase 7 validation failed: missing required files.")

    if args.check_api and not report.get("api_ok"):
        raise SystemExit(
            "Phase 7 API check failed. Start the backend: python -m phase6.validate --serve"
        )

    logger.info("Phase 7 validation passed.")


if __name__ == "__main__":
    main()
