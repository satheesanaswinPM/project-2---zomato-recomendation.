# Phase 7 — Next.js Frontend

Standalone Next.js UI that calls the Phase 6 backend API. No Python pipeline logic in this folder.

## Prerequisites

- Node.js 18+
- Phase 6 backend running on port 8000

## Setup

```powershell
cd phase7
copy .env.example .env.local
npm install
```

## Run

**Terminal 1 — Backend (from project root `zomato/`):**

```powershell
python -m phase6.validate --serve
```

**Terminal 2 — Frontend:**

```powershell
cd phase7
npm run dev
```

Open **http://localhost:3000**

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Phase 6 API base URL |

## Project structure

```
phase7/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # SearchForm, RecommendationCard, etc.
│   └── lib/              # API client + TypeScript types
├── package.json
├── .env.example
└── validate.py           # Structure smoke test
```

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Dev server on port 3000 |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |

## API integration

The frontend posts to `POST /api/recommendations` on the Phase 6 backend:

```json
{
  "location": "Marathahalli",
  "budget": "high",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_notes": "family-friendly"
}
```

Validation errors (400) are shown inline on form fields. Network failures show a banner. Results render as recommendation cards with rank, metadata, and AI explanation.

## Validation

```powershell
python -m phase7.validate
```

Checks required files exist. Use `--check-api` to verify the Phase 6 backend is reachable.
