import type {
  RecommendationsResponse,
  SearchPreferences,
} from "@/lib/types";

const DEFAULT_API_BASE = "http://localhost:8000";

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

  if (prefs.cuisine.trim()) {
    body.cuisine = prefs.cuisine.trim();
  }

  if (prefs.min_rating.trim()) {
    const rating = Number(prefs.min_rating);
    if (!Number.isNaN(rating)) {
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

export async function fetchRecommendations(
  prefs: SearchPreferences,
): Promise<RecommendationsResponse> {
  const url = `${getApiBaseUrl()}/api/recommendations`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toRequestBody(prefs)),
    });
  } catch {
    throw new ApiError(
      "Unable to reach the recommendation API. Is the Phase 6 backend running?",
    );
  }

  let payload: RecommendationsResponse;
  try {
    payload = (await response.json()) as RecommendationsResponse;
  } catch {
    throw new ApiError("Invalid response from the recommendation API.", response.status);
  }

  if (!response.ok && !("errors" in payload)) {
    throw new ApiError(
      "The recommendation API returned an unexpected error.",
      response.status,
    );
  }

  return payload;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${getApiBaseUrl()}/api/health`);
    if (!response.ok) {
      return false;
    }
    const data = (await response.json()) as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}
