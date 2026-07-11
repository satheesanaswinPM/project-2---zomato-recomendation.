# Culinary Compass — AI Zomato Restaurant Recommendations

AI-powered restaurant recommendation system inspired by Zomato. Users set preferences (Bangalore locality, budget, cravings, rating, required service); the app filters a real dataset and uses a **Groq LLM** to rank matches with human-readable explanations.

**Product UI:** Culinary Compass (Next.js) · **Free deploy path:** Streamlit Community Cloud

---

## Features

- Bangalore **locality** search (typeahead / selectbox from the dataset)
- Budget presets + **custom** max amount
- **Cravings** (cuisine) and **required service** notes
- **Groq** ranking with grounded “AI Match” explanations
- Natural language preference parsing (“Cheap Italian in Indiranagar, 4+ stars”)
- Follow-up refinement (“Show me cheaper options”)
- Search cache + recent history
- Two frontends: **Next.js** (API) and **Streamlit** (one-app free deploy)

---

## Architecture (phases)

| Phase | Name | Status |
|---|---|---|
| 1 | Data layer (Hugging Face / CSV cache) | Done |
| 2 | Preference validation | Done |
| 3 | Filter + LLM prompts | Done |
| 4 | Groq recommendation engine | Done |
| 5 | Display payload / renderers | Done |
| 6 | Flask JSON REST API | Done |
| 7 | Next.js Culinary Compass UI | Done |
| 8 | NL input, follow-ups, caching | Done |
| 9 | Streamlit free deploy app | Done |

Details: [`zomato/architecture.md`](zomato/architecture.md) · Problem statement: [`zomato/problemstatement.md`](zomato/problemstatement.md)

```
Next.js (phase7) ──HTTP──► Flask API (phase6) ──imports──► phases 1–5 (+ 8)
Streamlit (phase9) ────────────────────────────imports──► phase6 orchestrator
```

---

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Next.js UI)
- [Groq API key](https://console.groq.com)

### 1. Install Python deps

```powershell
cd zomato
pip install -r requirements.txt
```

### 2. Configure secrets

```powershell
copy .env.example .env
# Set GROQ_API_KEY=... in .env
# Or put the key in phase4/.env
```

### 3a. Full stack (API + Next.js)

**Terminal 1 — Backend**

```powershell
cd zomato
python -m phase6.validate --serve
```

API: http://127.0.0.1:8000

**Terminal 2 — Frontend**

```powershell
cd zomato/phase7
copy .env.example .env.local
npm install
npm run dev
```

App: http://localhost:3000

### 3b. Streamlit (single app, free-cloud friendly)

```powershell
cd zomato
pip install -r phase9/requirements.txt
python -m streamlit run phase9/app.py
```

App: http://localhost:8501

Deploy guide: [`zomato/phase9/README.md`](zomato/phase9/README.md)

---

## API overview (Phase 6)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/locations?city=Bangalore` | Bangalore localities |
| `POST` | `/api/recommendations` | Ranked recommendations |
| `POST` | `/api/parse-preferences` | NL → structured prefs |
| `POST` | `/api/refine` | Follow-up refinement |
| `GET` | `/api/history` | Recent cached searches |

Example:

```powershell
curl -X POST http://127.0.0.1:8000/api/recommendations `
  -H "Content-Type: application/json" `
  -d '{"location":"Indiranagar","budget":"medium","cuisine":"Italian","min_rating":4}'
```

---

## Project layout

```
zomato/
├── phase1/ … phase5/   # Core Python pipeline
├── phase6/             # Flask REST API
├── phase7/             # Next.js frontend
├── phase8/             # NL, refine, cache
├── phase9/             # Streamlit deploy app
├── architecture.md
├── problemstatement.md
├── requirements.txt
└── .env.example
```

---

## Validation

```powershell
cd zomato
python -m phase1.validate
python -m phase2.validate
python -m phase3.validate
python -m phase4.validate          # add --live for Groq
python -m phase5.validate
python -m phase6.validate
python -m phase8.validate
python -m phase9.validate
```

Frontend structure check:

```powershell
python -m phase7.validate
```

---

## Dataset

[ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

Cached locally under `phase1/cache/` (gitignored). First run may download from Hugging Face.

---

## Tech stack

| Layer | Stack |
|---|---|
| Data / pipeline | Python, pandas, Hugging Face Hub |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Backend | Flask |
| Frontend | Next.js, React, TypeScript, Tailwind |
| Free deploy | Streamlit Community Cloud |

---

## License / notes

- Do not commit `.env`, `phase4/.env`, or `phase9/.streamlit/secrets.toml`.
- Groq usage is subject to Groq’s free-tier limits.
