import type {
  ParsedPreferencesResponse,
  RecommendationsResponse,
  RefineResponse,
  SearchHistoryItem,
  SearchPreferences,
} from "@/lib/types";
import { historyLabel } from "@/lib/types";

const DEFAULT_API_BASE = "http://localhost:8000";
const HISTORY_KEY = "culinary-compass-history-v1";

export function getApiBaseUrl(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
    DEFAULT_API_BASE
  );
}

function toRequestBody(prefs: SearchPreferences): Record<string, string | number> {
  const body: Record<string, string | number> = {
    location: prefs.location.trim(),
    budget: prefs.budget,
  };

  if (prefs.budget === "custom" && prefs.max_budget.trim()) {
    const amount = Number(prefs.max_budget);
    if (!Number.isNaN(amount)) {
      body.max_budget = amount;
    }
  }

  if (prefs.cuisine.trim()) {
    body.cuisine = prefs.cuisine.trim();
  }

  if (prefs.min_rating.trim()) {
    const rating = Number(prefs.min_rating);
    if (!Number.isNaN(rating) && rating > 0) {
      body.min_rating = rating;
    }
  }

  if (prefs.additional_notes.trim()) {
    body.additional_notes = prefs.additional_notes.trim();
  }

  return body;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "Unable to reach the recommendation API. Is the Phase 6 backend running?",
    );
  }

  let payload: T;
  try {
    payload = (await response.json()) as T;
  } catch {
    throw new ApiError("Invalid response from the recommendation API.", response.status);
  }

  return payload;
}

export async function fetchRecommendations(
  prefs: SearchPreferences,
  options?: { sessionId?: string | null; queryLabel?: string },
): Promise<RecommendationsResponse> {
  const body: Record<string, unknown> = {
    ...toRequestBody(prefs),
    use_cache: true,
  };
  if (options?.sessionId) {
    body.session_id = options.sessionId;
  }
  if (options?.queryLabel) {
    body.query_label = options.queryLabel;
  }

  const payload = await postJson<RecommendationsResponse>(
    "/api/recommendations",
    body,
  );

  if (!("ok" in payload)) {
    throw new ApiError("Unexpected recommendation response.");
  }

  if (!payload.ok && !("errors" in payload)) {
    throw new ApiError("The recommendation API returned an unexpected error.");
  }

  return payload;
}

export async function parseNaturalLanguage(
  query: string,
): Promise<ParsedPreferencesResponse> {
  return postJson<ParsedPreferencesResponse>("/api/parse-preferences", {
    query,
  });
}

export async function refineSearch(
  sessionId: string,
  followUp: string,
): Promise<RefineResponse> {
  return postJson<RefineResponse>("/api/refine", {
    session_id: sessionId,
    follow_up: followUp,
  });
}

export async function fetchLocations(
  city: string = "Bangalore",
): Promise<string[]> {
  const url = `${getApiBaseUrl()}/api/locations?city=${encodeURIComponent(city)}`;

  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new ApiError(
      "Unable to reach the recommendation API. Is the Phase 6 backend running?",
    );
  }

  if (!response.ok) {
    throw new ApiError("Failed to load location list.", response.status);
  }

  const payload = (await response.json()) as {
    ok?: boolean;
    locations?: string[];
  };
  return payload.locations ?? [];
}

export function loadLocalHistory(): SearchHistoryItem[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as SearchHistoryItem[];
    return Array.isArray(parsed) ? parsed.slice(0, 8) : [];
  } catch {
    return [];
  }
}

export function saveLocalHistory(items: SearchHistoryItem[]): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 8)));
}

export function pushLocalHistory(
  prefs: SearchPreferences,
  existing: SearchHistoryItem[],
): SearchHistoryItem[] {
  const item: SearchHistoryItem = {
    label: historyLabel(prefs),
    preferences: { ...prefs },
    created_at: Date.now(),
  };
  const next = [
    item,
    ...existing.filter((entry) => entry.label !== item.label),
  ].slice(0, 8);
  saveLocalHistory(next);
  return next;
}

export function clearLocalHistory(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(HISTORY_KEY);
}
