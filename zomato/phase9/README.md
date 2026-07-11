# Phase 9 — Streamlit Deployment

Free, shareable Culinary Compass demo. One Python process — no separate Next.js or Flask server required.

## Local run

```powershell
cd "c:\nextleap projects\project 1 - zomato\zomato"
pip install -r phase9/requirements.txt

# Optional: local Streamlit secrets
copy phase9\.streamlit\secrets.toml.example phase9\.streamlit\secrets.toml
# Edit secrets.toml and set GROQ_API_KEY

# Or use existing phase4/.env / root .env
streamlit run phase9/app.py
```

Open **http://localhost:8501**

Validation (no browser):

```powershell
python -m phase9.validate
```

## Features

| Control | Notes |
|---|---|
| Location | Bangalore localities from `RestaurantStore.localities()` |
| Budget | low / medium / high / custom amount |
| Cravings | Cuisine text |
| Minimum rating | Any, 2.5+ … 5.0+ |
| Required service | Free-text notes |
| Natural language | Optional expander → parses via Phase 8 into preferences |

Search calls `phase6.orchestrator.run_recommendation_search()` (phases 1–5 + Groq).

## Streamlit Community Cloud (free)

1. Push this repo to GitHub (public).
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Settings:
   - **Repository:** your fork/repo
   - **Branch:** `main`
   - **Main file path:** `zomato/phase9/app.py`
   - **Python version:** 3.11+ recommended
4. **Advanced settings → Secrets:**

```toml
GROQ_API_KEY = "your_real_key"
```

5. Deploy. Share the `*.streamlit.app` URL.

### Dataset on Cloud

- Prefer committing or uploading `phase1/cache/zomato_raw.csv` if policy allows (large file), **or**
- Let the app download from Hugging Face on first boot (slower cold start).

`phase1/cache/` is gitignored locally — for Cloud you may need to generate the cache in CI, use Hugging Face download, or store the CSV via another artifact.

## Project layout

```
phase9/
├── app.py
├── ui.py
├── requirements.txt
├── validate.py
├── README.md
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Notes

- Do **not** commit `.streamlit/secrets.toml` with a real key.
- Phase 6 + 7 remain the primary API + Next.js stack; Phase 9 is the free one-app deploy path.
