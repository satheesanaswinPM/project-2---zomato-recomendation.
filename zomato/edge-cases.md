# Edge Cases: Zomato Recommendation System

Detailed edge cases derived from [problemstatement.md](./problemstatement.md) and [architecture.md](./architecture.md). Use this document for validation logic, test cases, and fallback design.

---

## How to Read This Document

Each edge case includes:

| Field | Meaning |
|---|---|
| **ID** | Unique reference for tests and issues |
| **Scenario** | What goes wrong or is unusual |
| **Example** | Concrete input or data state |
| **Expected Behavior** | What the system should do |
| **Priority** | `Critical` · `High` · `Medium` · `Low` |

---

## Phase 1 — Data Layer

### 1.1 Dataset Loading & Availability

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-D01 | Hugging Face dataset unreachable | Network offline during first load | Show clear error; use local CSV cache if available; otherwise fail gracefully with retry instructions | Critical |
| EC-D02 | Dataset schema changed on Hugging Face | New column names or removed fields | Validate expected columns on load; fail with schema mismatch message listing missing fields | Critical |
| EC-D03 | Empty dataset returned | 0 rows after download | Abort startup; log error; do not proceed to recommendation flow | Critical |
| EC-D04 | Partial download / corrupted file | Truncated CSV or broken cache | Detect via row count checksum or parse error; re-download automatically once | High |
| EC-D05 | Hugging Face rate limit or auth failure | 429 / 401 from API | Retry with backoff; instruct user to set HF token if required | High |
| EC-D06 | Dataset version drift | Cached data from older version | Store dataset version/hash in cache metadata; warn if remote version differs | Low |

### 1.2 Missing & Invalid Field Values

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-D07 | Missing restaurant name | `name: null` | Drop row; increment dropped-row counter; log at debug level | Critical |
| EC-D08 | Missing location / city | `location: ""` | Drop row — location is required for filtering | Critical |
| EC-D09 | Missing rating | `rating: null` | Option A: drop row. Option B: impute with city median. Document chosen strategy | High |
| EC-D10 | Missing cost for two | `cost_for_two: null` | Exclude from budget filter; include only if other filters match; flag as "price unavailable" in output | High |
| EC-D11 | Rating out of valid range | `rating: 6.5` or `-1` | Clamp to [0, 5] or drop row; log anomaly | Medium |
| EC-D12 | Cost stored as string | `"₹1,200 for two"` | Strip currency symbols and commas; parse to integer; drop if unparseable | High |
| EC-D13 | Duplicate restaurant entries | Same name + location twice | Deduplicate keeping highest vote count or latest rating | Medium |
| EC-D14 | Empty cuisine field | `cuisine: ""` | Set to `["Unknown"]`; still eligible unless user filters by cuisine | Medium |
| EC-D15 | Extremely long restaurant name | 500+ character string | Truncate for display; keep full name in store for matching | Low |

### 1.3 Normalization & Data Quality

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-D16 | City name aliases | `Bangalore` vs `Bengaluru` vs `BLR` | Maintain alias map; normalize to canonical city name before indexing | Critical |
| EC-D17 | Case-insensitive city mismatch | `delhi` vs `Delhi` vs `DELHI` | Lowercase + title-case normalization on ingest and query | Critical |
| EC-D18 | Cuisine as compound string | `"North Indian, Chinese, Mughlai"` | Split on comma/semicolon; trim whitespace; store as list | High |
| EC-D19 | Cuisine spelling variants | `North Indian` vs `North-Indian` vs `north indian` | Normalize to lowercase slug for matching; display original label | High |
| EC-D20 | Rating with few votes | `rating: 5.0, votes: 1` | Optionally deprioritize in sort (Bayesian average) or flag "low confidence" | Medium |
| EC-D21 | Identical ratings across many restaurants | 50 restaurants all at 4.2 | Secondary sort by votes, then name; ensure deterministic ordering | Medium |
| EC-D22 | Special characters in names | `"McDonald's"`, `"Café 999"`, emoji in name | Preserve UTF-8; escape properly in JSON prompts | Medium |
| EC-D23 | Restaurant listed under wrong city | Data quality issue in source | No fix at ingest; surface in output as-is; do not override | Low |

### 1.4 Query & Store Edge Cases

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-D24 | Query city not in dataset | User asks for `Goa` but dataset has no Goa rows | Return empty candidate set; trigger Phase 3 empty-state fallback | Critical |
| EC-D25 | City exists but has very few restaurants | `Puducherry` with 3 entries | Return all available; do not pad with other cities | High |
| EC-D26 | Large result set for popular city | `Bangalore` with 5,000+ restaurants | Filter pipeline must reduce before LLM; never send full city to LLM | Critical |
| EC-D27 | Concurrent reads during reload | Data refresh while request in flight | Use immutable snapshot or read lock; avoid partial state | Medium |

---

## Phase 2 — User Input

### 2.1 Required Field Validation

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-U01 | Missing location | `location: ""` | Reject with message: "Location is required" | Critical |
| EC-U02 | Missing budget | Budget field skipped | Reject with message: "Budget is required (low / medium / high)" | Critical |
| EC-U03 | Invalid budget value | `budget: "cheap"` or `"premium"` | Reject; list valid options: low, medium, high | Critical |
| EC-U04 | Whitespace-only location | `location: "   "` | Treat as empty; reject as EC-U01 | High |
| EC-U05 | Location with leading/trailing spaces | `" Bangalore "` | Trim whitespace before validation and matching | High |

### 2.2 Optional Field Validation

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-U06 | min_rating not provided | Field omitted | Default to `0` (no rating filter) | High |
| EC-U07 | min_rating out of range | `min_rating: 6` or `-2` | Reject; valid range 0.0 – 5.0 | High |
| EC-U08 | min_rating with too many decimals | `min_rating: 4.123456` | Round to 1 decimal place or reject based on policy | Low |
| EC-U09 | Cuisine not provided | Field omitted | Skip cuisine filter; match all cuisines in location | High |
| EC-U10 | Empty cuisine string | `cuisine: ""` | Treat same as omitted — no cuisine filter | Medium |
| EC-U11 | Additional notes not provided | Field omitted | Pass empty string to LLM prompt | Medium |
| EC-U12 | Additional notes very long | 5,000 character essay | Truncate to token-safe limit (e.g., 500 chars) with warning | Medium |

### 2.3 Location & Cuisine Input Variants

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-U13 | City alias entered by user | User types `Bengaluru` | Resolve via alias map to canonical form | Critical |
| EC-U14 | City not in dataset | User types `Shimla` | Accept input as valid format; empty results handled downstream with helpful message | Critical |
| EC-U15 | Misspelled city | `Banglore`, `Dheli` | Fuzzy match against known cities; suggest correction if close match found | Medium |
| EC-U16 | User enters locality instead of city | `Koramangala` instead of `Bangalore` | If locality not in schema, treat as city filter; return empty or partial match with guidance | High |
| EC-U17 | Cuisine case mismatch | `italian` vs `Italian` | Case-insensitive match against dataset cuisine values | High |
| EC-U18 | Cuisine not in dataset | `Mexican` in a dataset with no Mexican restaurants | Accept input; filter returns zero; suggest relaxing cuisine | High |
| EC-U19 | Partial cuisine match | User: `Indian`; dataset: `North Indian`, `South Indian` | Substring or token match policy — document whether `Indian` matches both | High |
| EC-U20 | Multiple cuisines requested | `Italian, Chinese` | Define policy: AND (must serve both) vs OR (either). Recommend OR with ranking boost for both | Medium |

### 2.4 Input Interface Edge Cases

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-U21 | User aborts mid-input (CLI) | Ctrl+C during prompt | Exit cleanly without partial API call | Medium |
| EC-U22 | Non-interactive environment | Piped empty stdin | Fail with usage instructions | Medium |
| EC-U23 | SQL/script injection in text fields | `'; DROP TABLE--` in notes | Sanitize for display; never execute; pass as plain text to LLM | High |
| EC-U24 | Unicode / emoji in notes | `"Romantic place 💕 near park"` | Accept UTF-8; include in prompt as-is | Low |
| EC-U25 | Conflicting preferences in notes | Budget: low; notes: "luxury fine dining" | LLM may rank differently; prefer structured filters as hard constraints, notes as soft signal | Medium |

---

## Phase 3 — Integration Layer (Filtering & Prompts)

### 3.1 Filter Pipeline — Zero & Low Results

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-F01 | Zero restaurants match all filters | High budget + Italian + 4.8 rating in small city | Return empty set; message: "No matches. Try lowering rating or changing cuisine." | Critical |
| EC-F02 | Zero after location filter only | City not in dataset | Suggest available cities from dataset | Critical |
| EC-F03 | Filters match exactly 1 restaurant | Only one North Indian in budget range | Return single candidate; LLM ranks 1 item; display 1 result | High |
| EC-F04 | Filters match 2–4 restaurants | Fewer than requested top 5 | Return all available; do not duplicate or invent extras | High |
| EC-F05 | Filters match 500+ restaurants | Broad search in Mumbai | Apply top-N cap (15–20) sorted by rating/votes before LLM | Critical |

### 3.2 Filter Logic Conflicts

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-F06 | Budget excludes all high-rated options | Low budget + min_rating 4.8 in expensive city | Return empty or few results; suggest raising budget or lowering rating | High |
| EC-F07 | Cuisine filter too strict (AND logic) | User wants Italian AND Chinese | If AND returns zero, optionally retry with OR and inform user | Medium |
| EC-F08 | min_rating filters out all but unrated | Rating missing on all budget matches | Exclude null-rating rows from min_rating filter; explain in output | High |
| EC-F09 | Cost missing for budget filter | `cost_for_two: null` | Policy: exclude from budget filter OR treat as unknown bucket — document choice | High |
| EC-F10 | Budget boundary values | Cost exactly ₹500 or ₹1500 | Define inclusive/exclusive boundaries consistently (e.g., low ≤ 500, medium 501–1500) | High |

### 3.3 Candidate Formatting & Token Limits

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-F11 | Candidate list exceeds LLM context window | 20 restaurants × long descriptions | Send compact JSON (name, rating, cost, cuisine only); strip verbose fields | Critical |
| EC-F12 | Total prompt exceeds token limit | Long additional_notes + 20 candidates | Reduce N candidates iteratively until within limit | Critical |
| EC-F13 | Special characters break JSON in prompt | Restaurant name: `"The "Best" Biryani"` | Properly escape quotes in serialized candidate JSON | High |
| EC-F14 | Duplicate names in candidate list | Two `"Spice Garden"` in same city | Include disambiguator (location, rating) in prompt; match by name + metadata in guard | High |
| EC-F15 | All candidates have identical metadata | Same rating, cost, cuisine | LLM ranking acceptable; fallback sort by name for determinism | Low |

### 3.4 Prompt & Fallback Behavior

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-F16 | Progressive filter relaxation needed | Strict filters → 0 results | Auto-relax in order: rating → cuisine → budget; tell user what was relaxed | High |
| EC-F17 | User notes mention unavailable attributes | "Outdoor seating" not in dataset | Pass note to LLM as preference; do not hard-filter; LLM explains uncertainty | Medium |
| EC-F18 | Empty candidate list reaches LLM | Bug bypasses guard | Block LLM call; return user message immediately | Critical |
| EC-F19 | Single candidate with contradictory prefs | Low budget but only expensive restaurant matched after relaxation | LLM explains compromise; flag as "closest match" | Medium |

---

## Phase 4 — Recommendation Engine (LLM)

### 4.1 API & Infrastructure Failures

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-L01 | LLM API key missing | `OPENAI_API_KEY` not set | Fail fast with setup instructions; do not call API | Critical |
| EC-L02 | LLM API key invalid | 401 Unauthorized | Clear error; no retry loop | Critical |
| EC-L03 | LLM request timeout | No response in 30s | Retry once; then fallback to rating-based sort with template explanations | Critical |
| EC-L04 | Rate limit exceeded | 429 Too Many Requests | Exponential backoff retry (max 2); then fallback | High |
| EC-L05 | LLM service unavailable | 503 from provider | Fallback to deterministic ranking; show "AI unavailable" notice | Critical |
| EC-L06 | Network interruption mid-request | Connection reset | Retry once; fallback on second failure | High |
| EC-L07 | Partial streaming response (if streaming) | Truncated JSON | Treat as invalid response; re-prompt or fallback | Medium |

### 4.2 Response Parsing Failures

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-L08 | LLM returns plain text instead of JSON | Prose paragraph ranking | Attempt JSON extraction from markdown code block; re-prompt once if fails | Critical |
| EC-L09 | Malformed JSON | Missing bracket, trailing comma | Re-prompt with stricter format; fallback if second attempt fails | Critical |
| EC-L10 | Empty JSON array | `[]` | Fallback to top-N by rating with template explanations | High |
| EC-L11 | Wrong JSON schema | Returns `{restaurants: [...]}` instead of expected shape | Map known alternate shapes; fallback if unmappable | High |
| EC-L12 | Missing required fields in item | `{rank: 1}` without name | Skip invalid items; fill from candidate list if rank matches | High |
| EC-L13 | Duplicate ranks | Two items with `rank: 1` | Re-number sequentially; preserve relative order | Medium |
| EC-L14 | Non-sequential ranks | Ranks 1, 3, 7 | Re-number 1..N for display | Low |
| EC-L15 | LLM returns more than 5 items | 10 recommendations | Take top 5 by rank; discard rest | Medium |
| EC-L16 | LLM returns fewer than 3 items | Only 1 recommendation | Display what was returned; optionally pad with rating fallback | Medium |

### 4.3 Hallucination & Grounding

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-L17 | LLM invents restaurant not in candidates | `"The Golden Fork"` not in list | Strip from results; log warning; backfill from next valid candidate | Critical |
| EC-L18 | LLM slightly misspells candidate name | `"Spice Garten"` vs `"Spice Garden"` | Fuzzy match against candidate list (Levenshtein threshold); attach correct metadata | Critical |
| EC-L19 | LLM recommends all candidates unranked | Same explanation for each | Accept but re-sort by rating; flag low-quality LLM output | Medium |
| EC-L20 | LLM ignores budget in explanation | Says "fits your luxury budget" for low budget | Explanations are soft; structured data in output must reflect actual cost | High |
| EC-L21 | LLM claims attribute not in data | "Has outdoor seating" when dataset has no such field | Prefer explanations citing known fields only; add disclaimer in prompt | Medium |
| EC-L22 | LLM refuses to answer | "I cannot recommend restaurants" | Re-prompt with simplified instruction; fallback on repeat | High |
| EC-L23 | LLM outputs harmful / off-topic content | Unrelated text | Discard response; fallback; do not display raw LLM output | High |

### 4.4 Explanation Quality

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-L24 | Empty explanation string | `"explanation": ""` | Replace with template: "Rated X with cuisine Y in your budget range." | Medium |
| EC-L25 | Explanation too long | 800-word essay per restaurant | Truncate to display limit (e.g., 200 chars) with ellipsis | Medium |
| EC-L26 | Explanation contradicts user prefs | Recommends expensive place for low budget user | Keep restaurant if passed filters; rewrite explanation from metadata if detected | Medium |
| EC-L27 | Summary missing when optional summary requested | No overview paragraph | Generate template summary from top 3 names and cuisines | Low |

---

## Phase 5 — Output Display

### 5.1 Display & Formatting

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-O01 | Missing cost in result metadata | `cost_for_two: null` | Display "Price not available" instead of blank or `null` | High |
| EC-O02 | Missing cuisine | Empty cuisine list | Display "Cuisine not listed" | Medium |
| EC-O03 | Very long restaurant name in narrow UI | 80+ char name | Wrap or truncate with tooltip/full name on hover | Low |
| EC-O04 | Rating displayed with excess precision | `4.333333` | Format to 1 decimal: `4.3` | Low |
| EC-O05 | Zero recommendations to display | Empty result set | Show empty-state UI with filter relaxation suggestions | Critical |
| EC-O06 | Partial field set from fallback engine | Template explanation only | Still show all structured fields from dataset; mark as "AI summary unavailable" | High |
| EC-O07 | Unicode rendering in terminal (CLI) | `"Mahesh's Thali – ₹800"` | Ensure UTF-8 stdout; fallback ASCII if terminal unsupported | Medium |

### 5.2 User-Facing Error States

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-O08 | LLM fallback used | AI unavailable | Clearly label: "Ranked by rating (AI explanations unavailable)" | High |
| EC-O09 | Filters were auto-relaxed | Rating lowered automatically | Inform user: "No exact matches; showing results with rating ≥ 3.5" | High |
| EC-O10 | Single result displayed | Only 1 match | Show as #1 without implying more exist | Medium |
| EC-O11 | Internal error during render | Template crash | Generic user message; log stack trace internally | Critical |

---

## Phase 6 — Stretch Goals (Optional)

### 6a — Natural Language Input

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-N01 | Ambiguous NL query | "Good food near me" | Ask clarifying question for location; no "near me" without geo | High |
| EC-N02 | NL query missing budget | "Italian in Bangalore" | Infer medium budget default or prompt user to confirm | Medium |
| EC-N03 | NL parser extracts wrong city | Misparse `Banaras` as `Bangalore` | Confirm extracted prefs with user before search | High |
| EC-N04 | NL query in mixed language | Hinglish input | Best-effort parse; fallback to structured form | Low |
| EC-N05 | NL parser LLM fails | Same as EC-L03 | Fallback to structured CLI/API input form | High |

### 6b — Follow-Up / Refinement

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-N06 | Follow-up without session context | "Show cheaper options" on new session | Prompt user to run initial search first | High |
| EC-N07 | Contradictory follow-up | Initial: low budget → "Show premium places" | Update budget pref; re-run filter; explain change | Medium |
| EC-N08 | Follow-up filters to zero results | "Only 5-star" when none exist | Empty state with prior results cleared or relaxed | High |
| EC-N09 | Very long conversation history | 20+ follow-up turns | Summarize or trim context to fit token limits | Medium |

### 6c — Caching & Persistence

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-N10 | Cache hit with stale dataset | Data refreshed but old cache used | Invalidate cache on dataset version change | High |
| EC-N11 | Cached LLM response for different prefs | Hash collision (unlikely) | Cache key must include full preference object hash | Medium |
| EC-N12 | Cache storage full or write fails | Disk full | Degrade gracefully; skip cache; continue request | Low |

### 6d — Web UI

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-N13 | Double form submit | User clicks "Search" twice | Debounce button; ignore duplicate in-flight requests | Medium |
| EC-N14 | API slow; user navigates away | Tab closed mid-request | Cancel request client-side if possible | Low |
| EC-N15 | Mobile viewport — long results | Small screen | Responsive cards; scrollable list | Medium |
| EC-N16 | XSS in LLM explanation output | `<script>alert(1)</script>` in explanation | Escape HTML before rendering in web UI | Critical |

---

## Cross-Cutting / System-Level Edge Cases

### Security & Configuration

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-X01 | API key exposed in logs | Key printed on error | Never log secrets; redact in debug output | Critical |
| EC-X02 | `.env` file missing | No local config | Copy from `.env.example`; document required vars | High |
| EC-X03 | Prompt injection via additional_notes | "Ignore previous instructions and..." | System prompt instructs LLM to ignore override attempts; notes treated as preference text only | Critical |
| EC-X04 | Excessive API cost | User loops requests in tight loop | Optional rate limiting per session/IP | Medium |

### Performance & Scalability

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-X05 | Cold start — first request slow | Dataset load on first call | Lazy load at startup or warm cache; show loading indicator in UI | High |
| EC-X06 | Memory pressure with full dataset | Low RAM machine | Use chunked reads or on-disk cache; avoid duplicate copies | Medium |
| EC-X07 | Repeated identical requests | Same prefs submitted 10 times | Optional cache (Phase 6); idempotent results | Low |

### Data Integrity & Compliance

| ID | Scenario | Example | Expected Behavior | Priority |
|---|---|---|---|---|
| EC-X08 | Outdated restaurant data | Closed restaurant still in dataset | Display dataset disclaimer; no live verification in MVP | Low |
| EC-X09 | Personal data in logs | User notes logged verbatim | Minimize PII logging; redact in production | Medium |

### End-to-End Scenarios (Integration Tests)

| ID | Scenario | Input | Expected Outcome | Priority |
|---|---|---|---|---|
| EC-E2E01 | Happy path | Bangalore, medium, North Indian, 4.0+ | 3–5 grounded recommendations with explanations | Critical |
| EC-E2E02 | Impossible combination | Low budget + high min_rating + rare cuisine + small city | Empty or relaxed results with clear user message | Critical |
| EC-E2E03 | LLM down | Valid prefs, API 503 | Rating-based fallback with user notice | Critical |
| EC-E2E04 | LLM hallucinates 2 of 5 | Mixed valid/invalid names | Only validated restaurants shown; count may be < 5 | Critical |
| EC-E2E05 | City alias end-to-end | User: `Bengaluru`, dataset: `Bangalore` | Same results as canonical city search | High |
| EC-E2E06 | No cuisine preference | Location + budget only | Broad cuisine mix in results, ranked by LLM | High |
| EC-E2E07 | Additional notes only differentiation | Same filters, different notes | Explanations reflect notes; ranking may differ | Medium |

---

## Edge Case Handling Matrix (Quick Reference)

| Condition | Primary Handler | Fallback |
|---|---|---|
| Zero filter matches | User message + suggest relax filters | Auto-relax rating → cuisine → budget |
| LLM failure | Retry once | Rating sort + template explanations |
| Hallucinated restaurant | Fuzzy match → strip → backfill | Fill from next candidate by rating |
| Missing data field | Default label in UI | Exclude from filter if critical |
| Invalid user input | Validation error before API call | Suggest valid options |
| Token limit exceeded | Reduce candidate count N | Truncate additional_notes |

---

## Recommended Test Priority

### Must test before MVP (Critical + High)

- EC-D01, EC-D07, EC-D16, EC-D17, EC-D24, EC-D26
- EC-U01, EC-U02, EC-U03, EC-U13, EC-U14, EC-U17
- EC-F01, EC-F05, EC-F10, EC-F11, EC-F18
- EC-L01, EC-L03, EC-L08, EC-L17, EC-L18
- EC-O05, EC-O08
- EC-E2E01, EC-E2E02, EC-E2E03, EC-E2E04

### Test before production / web UI

- EC-N16, EC-X01, EC-X03, EC-L23

### Test when stretch goals are implemented

- EC-N01 – EC-N09, EC-N10 – EC-N12

---

## Related Documents

- [problemstatement.md](./problemstatement.md) — project requirements and workflow
- [architecture.md](./architecture.md) — phase-wise components and error handling overview
