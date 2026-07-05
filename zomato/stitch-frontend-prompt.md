# Google Stitch Prompt — Zomato Recommendation Frontend (Next.js)

Copy the prompt block below into [Google Stitch](https://stitch.withgoogle.com) to generate high-fidelity UI mockups for the Phase 7 frontend.

**Target stack:** Next.js 14+ (App Router), React, TypeScript, Tailwind CSS  
**Backend:** Separate REST API at `http://localhost:8000` (not part of this UI)

---

## How to use with Stitch

1. Paste **Prompt 1** first to generate the main search + results screen.
2. Paste **Prompt 2** to generate the loading state variant.
3. Paste **Prompt 3** for the empty / error state variant.
4. Keep the same project in Stitch so colors and typography stay consistent.

---

## Prompt 1 — Main screen (search form + recommendations)

```
Design a modern restaurant recommendation web app inspired by Zomato. This is a Next.js frontend that calls a JSON REST API — no backend logic in the UI.

VIBE:
Clean, trustworthy food-discovery app. Warm and appetizing but not cluttered. Professional SaaS polish with Zomato-inspired energy. Desktop-first, fully responsive down to mobile.

DESIGN SYSTEM (REQUIRED):
- Platform: Web, desktop-first, responsive to 375px mobile
- Framework target: Next.js App Router + Tailwind CSS
- Primary brand: Zomato Red (#E23744) — primary CTA buttons, rank badges, focus rings
- Primary hover: Deep Red (#CB2F3B)
- Background: Soft gray (#F6F7FB)
- Surface / cards: White (#FFFFFF) with subtle shadow (0 2px 12px rgba(0,0,0,0.08))
- Text primary: Dark navy (#1A1A2E)
- Text secondary: Medium gray (#555555)
- Error: Crimson (#C0392B) for validation messages and error borders
- Info notice: Light blue (#EEF6FF) with border (#B8D4F0)
- Warning notice: Light amber (#FFF8E6) with border (#F0D78C)
- Typography: System UI / Inter — H1 28px semibold, body 16px, labels 14px semibold
- Border radius: 12px cards, 8px inputs and buttons
- Spacing: 8px grid, generous whitespace, max content width 720px centered

PAGE STRUCTURE:

1. HEADER (top of page, no heavy nav bar):
   - App title: "Restaurant Finder"
   - Subtitle: "Enter your preferences and get personalized AI recommendations."
   - No logo required; keep minimal

2. SEARCH PANEL (white card, full width within container):
   - Section title: "Your preferences"
   - Form fields in a single column on mobile, two columns on desktop where appropriate:
     a) Location * — text input, placeholder "e.g. Marathahalli, Bangalore"
     b) Budget * — dropdown select with options:
        - Low (Rs.0 - Rs.500)
        - Medium (Rs.501 - Rs.1,500)
        - High (Rs.1,501+)
     c) Cuisine — text input, placeholder "e.g. Italian, North Indian"
     d) Minimum rating — number input 0–5, step 0.1, placeholder "0 - 5"
     e) Additional notes — textarea, 3 rows, placeholder "e.g. family-friendly, quick service"
   - Primary CTA button (full width on mobile): "Find restaurants" — Zomato Red background, white text, 48px height
   - Show inline validation error text below fields in red when invalid (example: "Location is required.")

3. RESULTS PANEL (white card below form, visible after search):
   - Section heading: "Your Recommendations"
   - Summary line at top (gray text): "Top recommendations for you: The Black Pearl, Onesta, and 3 more."
   - Vertical list of 5 recommendation cards

4. RECOMMENDATION CARD (repeat for each result):
   - Small rank label top-left: "#1" in Zomato Red, bold
   - Restaurant name as card title: e.g. "The Black Pearl" — 18px semibold
   - Metadata row with pill-style or dot-separated chips:
     - Location: "Bangalore"
     - Cuisine: "North Indian, European, BBQ"
     - Cost: "Rs.1500"
     - Rating: "4.8"
   - Explanation block with label "Why:" followed by 2–3 lines of AI-generated text:
     "High rating, great for family dining, fits your high budget and Italian preference."
   - Card background: very light gray (#FAFAFA), 1px border (#EEEEEE), 10px radius
   - Subtle hover elevation on desktop

5. FOOTER (minimal):
   - Small muted text: "Powered by AI · Data from Zomato dataset"
   - No heavy link columns

LAYOUT:
- Single-page scroll layout: header → search card → results card
- Centered container, max-width 720px, 32px vertical padding
- Cards stacked with 24px gap between sections

SAMPLE CONTENT (use realistic Indian restaurant names):
1. The Black Pearl — Bangalore — North Indian, European, BBQ — Rs.1500 — 4.8
2. Onesta — Bangalore — Pizza, Italian — Rs.600 — 4.6
3. Meghana Foods — Bangalore — Biryani, Andhra — Rs.800 — 4.5
4. Truffles — Bangalore — Burger, American — Rs.900 — 4.4
5. Barbeque Nation — Bangalore — BBQ, North Indian — Rs.1800 — 4.3

CONSTRAINTS:
- Do NOT include backend code, database UI, or admin panels
- Do NOT use dark mode
- Accessible contrast (WCAG AA), clear focus states on inputs
- No stock food photography required — typography and cards only
- Design should map cleanly to React components: SearchForm, RecommendationCard, ResultsSummary, ErrorMessage
```

---

## Prompt 2 — Loading state

```
Using the SAME design system as the Restaurant Finder app (Zomato Red #E23744, soft gray background #F6F7FB, white cards, Inter/system font, 720px centered layout):

Show the search form in a disabled/locked state while recommendations are loading.

CHANGES FROM MAIN SCREEN:
- "Find restaurants" button shows a loading spinner and text "Finding restaurants..."
- Button is disabled, slightly reduced opacity
- Below the form, show a results panel skeleton:
  - Section title: "Your Recommendations"
  - 3 skeleton placeholder cards with shimmer animation
  - Each skeleton: gray bars for rank, title, metadata chips, and explanation text
- Subtle helper text under button: "Analyzing restaurants with AI — this may take a few seconds"

Keep header, form fields (filled with sample values: Location "Marathahalli", Budget "High", Cuisine "Italian"), and footer identical to the main screen.
```

---

## Prompt 3 — Empty and error states

```
Using the SAME design system as the Restaurant Finder app (Zomato Red #E23744, soft gray background, white cards, 720px centered layout):

Design TWO states stacked vertically as separate sections (for documentation), OR as one screen with the error state most prominent:

STATE A — VALIDATION ERRORS (form still visible):
- Location field empty with red border and error: "Location is required."
- Budget dropdown invalid with error: "Budget must be one of: low, medium, high."
- Submit button remains enabled
- No results panel shown

STATE B — EMPTY RESULTS (after successful search, no matches):
- Results panel titled "Your Recommendations"
- Centered empty state illustration area (simple icon: magnifying glass or plate, line-art style, gray)
- Heading: "No restaurants found"
- Body text: "Try lowering your minimum rating, changing cuisine, or adjusting budget."
- Secondary outline button: "Adjust filters" (optional)

STATE C — API ERROR NOTICE:
- Light red info banner inside results panel (#FFF0F0, border #F0B8B8):
  "Something went wrong while fetching recommendations. Please try again."
- Retry button: "Try again" — outline style with red border

Use the same search form and header as the main screen. Mobile responsive.
```

---

## Prompt 4 — Mobile layout (optional refinement)

```
Refine the Restaurant Finder screen for mobile (375px width). Same Zomato-inspired design system.

MOBILE-SPECIFIC LAYOUT:
- Full-width cards with 16px horizontal padding
- Form fields single column, 16px vertical gap
- "Find restaurants" CTA sticky at bottom of viewport OR full-width below form
- Recommendation cards: metadata chips wrap to two lines
- Rank badge and restaurant name on same row
- Reduce H1 to 24px
- Touch-friendly 44px minimum tap targets

Show one filled search form and two recommendation cards with sample data.
```

---

## API contract (for developer handoff)

The Next.js frontend will call:

```
POST http://localhost:8000/api/recommendations
Content-Type: application/json

{
  "location": "Marathahalli",
  "budget": "high",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_notes": "family-friendly"
}
```

**Success response (200):**
```json
{
  "ok": true,
  "display": {
    "title": "Your Recommendations",
    "summary": "Top recommendations for you: ...",
    "message": null,
    "warnings": [],
    "source": "llm",
    "is_empty": false,
    "is_error": false,
    "recommendations": [
      {
        "rank": 1,
        "name": "The Black Pearl",
        "location": "Bangalore",
        "cuisine": "North Indian, European, BBQ",
        "cost_label": "Rs.1500",
        "rating_label": "4.8",
        "explanation": "High rating, within budget...",
        "source": "llm"
      }
    ]
  }
}
```

**Validation error (400):**
```json
{
  "ok": false,
  "errors": {
    "location": "Location is required."
  }
}
```

---

## Suggested Next.js component map

| Stitch section | React component |
|---|---|
| Header | `app/page.tsx` hero block |
| Search form | `components/SearchForm.tsx` |
| Loading skeleton | `components/ResultsSkeleton.tsx` |
| Results summary | `components/ResultsSummary.tsx` |
| Recommendation card | `components/RecommendationCard.tsx` |
| Empty / error | `components/EmptyState.tsx`, `components/ErrorBanner.tsx` |
| API client | `lib/api.ts` → `fetchRecommendations()` |

---

## Stitch refinement prompts (use one at a time)

After the first generation, iterate with short focused prompts:

- `"Make all buttons fully rounded (pill shape) and increase card shadow slightly."`
- `"Add subtle food-related line icons next to location, cuisine, cost, and rating metadata."`
- `"Change the primary font to Inter and increase line-height in explanation text for readability."`
- `"Add a thin top navigation bar with the app name on the left and a 'How it works' text link on the right."`
- `"Refrain from altering any other functionalities or design elements."` *(use when Stitch drifts)*
