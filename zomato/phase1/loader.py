"""Load the Zomato dataset from Hugging Face with local CSV caching."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DATASET_REVISION = "5738e9eda2fad49ad51c6e0ed26e761d9b947133"
CSV_FILENAME = "zomato.csv"

RAW_CACHE_FILENAME = "zomato_raw.csv"
RAW_CACHE_VERSION = "2"

REQUIRED_COLUMNS = [
    "name",
    "location",
    "cuisines",
    "approx_cost(for two people)",
    "rate",
    "votes",
    "rest_type",
    "address",
]

MAX_DOWNLOAD_ATTEMPTS = 3


def _cache_dir() -> Path:
    return Path(__file__).resolve().parent / "cache"


def _raw_cache_path() -> Path:
    return _cache_dir() / RAW_CACHE_FILENAME


def _version_marker_path() -> Path:
    return _cache_dir() / "raw_version.txt"


def _validate_schema(df: pd.DataFrame) -> None:
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset schema mismatch. Missing columns: {sorted(missing)}. "
            f"Found: {sorted(df.columns)}"
        )
    if df.empty:
        raise ValueError("Dataset is empty after load.")


def _download_source_csv() -> Path:
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise ImportError(
            "Install dependencies with: pip install -r phase1/requirements.txt"
        ) from exc

    last_error: Exception | None = None
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        try:
            logger.info(
                "Downloading dataset from Hugging Face (%s), attempt %d/%d",
                DATASET_ID,
                attempt,
                MAX_DOWNLOAD_ATTEMPTS,
            )
            return Path(
                hf_hub_download(
                    repo_id=DATASET_ID,
                    repo_type="dataset",
                    filename=CSV_FILENAME,
                    revision=DATASET_REVISION,
                )
            )
        except Exception as exc:
            last_error = exc
            logger.warning("Download attempt %d failed: %s", attempt, exc)
            if attempt < MAX_DOWNLOAD_ATTEMPTS:
                time.sleep(2 * attempt)

    raise RuntimeError(
        f"Failed to download dataset after {MAX_DOWNLOAD_ATTEMPTS} attempts."
    ) from last_error


def _download_csv_columns() -> pd.DataFrame:
    source_path = _download_source_csv()
    df = pd.read_csv(source_path, usecols=REQUIRED_COLUMNS)
    _validate_schema(df)
    logger.info("Loaded %d rows with %d columns", len(df), len(df.columns))
    return df


def _write_cache(df: pd.DataFrame) -> None:
    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(_raw_cache_path(), index=False)
    _version_marker_path().write_text(RAW_CACHE_VERSION, encoding="utf-8")
    logger.info("Cached raw dataset to %s (%d rows)", _raw_cache_path(), len(df))


def _read_cache() -> pd.DataFrame | None:
    cache_path = _raw_cache_path()
    version_path = _version_marker_path()
    if not cache_path.exists() or not version_path.exists():
        return None
    if version_path.read_text(encoding="utf-8").strip() != RAW_CACHE_VERSION:
        logger.warning("Cache version mismatch; will re-download dataset.")
        return None

    logger.info("Loading raw dataset from cache: %s", cache_path)
    df = pd.read_csv(cache_path)
    _validate_schema(df)
    return df


def load_raw_dataset(
    *,
    use_cache: bool = True,
    force_refresh: bool = False,
    source_path: Path | str | None = None,
) -> pd.DataFrame:
    """
    Load the raw Zomato dataset.

    Attempts local CSV cache first, then downloads required columns from Hugging Face.
    Pass source_path to load from a local CSV file (useful for tests).
    """
    if source_path is not None:
        path = Path(source_path)
        df = pd.read_csv(path, usecols=lambda col: col in REQUIRED_COLUMNS)
        _validate_schema(df)
        return df

    if use_cache and not force_refresh:
        cached = _read_cache()
        if cached is not None:
            return cached

    df = _download_csv_columns()
    if use_cache:
        _write_cache(df)
    return df
