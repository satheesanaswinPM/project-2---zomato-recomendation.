export type BudgetLevel = "low" | "medium" | "high" | "custom";

export interface SearchPreferences {
  location: string;
  budget: BudgetLevel | "";
  max_budget: string;
  cuisine: string;
  min_rating: string;
  additional_notes: string;
}

export interface DisplayRecommendation {
  rank: number;
  name: string;
  location: string;
  cuisine: string;
  cost_label: string;
  rating_label: string;
  explanation: string;
  source: string;
}

export interface DisplayPayload {
  title: string;
  summary: string | null;
  message: string | null;
  warnings: string[];
  source: string;
  is_empty: boolean;
  is_error: boolean;
  recommendations: DisplayRecommendation[];
}

export interface SuccessResponse {
  ok: true;
  display: DisplayPayload;
  session_id?: string | null;
  cache_hit?: boolean;
}

export interface ErrorResponse {
  ok: false;
  errors: Record<string, string>;
  message?: string;
}

export type RecommendationsResponse = SuccessResponse | ErrorResponse;

export interface ParsedPreferencesResponse {
  ok: boolean;
  preferences?: Record<string, unknown>;
  errors?: Record<string, string>;
  message?: string;
}

export interface RefineResponse {
  ok: boolean;
  session_id?: string;
  preferences?: Record<string, unknown>;
  display?: DisplayPayload;
  cache_hit?: boolean;
  errors?: Record<string, string>;
  message?: string;
}

export interface SearchHistoryItem {
  key?: string;
  label: string;
  preferences: SearchPreferences;
  created_at: number;
}

export const EMPTY_PREFERENCES: SearchPreferences = {
  location: "",
  budget: "",
  max_budget: "",
  cuisine: "",
  min_rating: "",
  additional_notes: "",
};

export const BUDGET_OPTIONS: { value: BudgetLevel; label: string }[] = [
  { value: "low", label: "Rs. 0 - 500" },
  { value: "medium", label: "Rs. 500 - 1,500" },
  { value: "high", label: "Rs. 1,501+" },
  { value: "custom", label: "Enter custom amount" },
];

export const RATING_OPTIONS: { value: string; label: string }[] = [
  { value: "0", label: "Any rating" },
  { value: "2.5", label: "2.5+" },
  { value: "3", label: "3.0+" },
  { value: "3.5", label: "3.5+" },
  { value: "4", label: "4.0+" },
  { value: "4.5", label: "4.5+" },
  { value: "5", label: "5.0+" },
];

export function preferencesFromApi(
  data: Record<string, unknown>,
): SearchPreferences {
  const budget = String(data.budget ?? "");
  const maxBudget =
    data.max_budget === null || data.max_budget === undefined
      ? ""
      : String(data.max_budget);
  const minRating =
    data.min_rating === null || data.min_rating === undefined
      ? ""
      : String(data.min_rating);

  return {
    location: String(data.location ?? ""),
    budget: (budget as SearchPreferences["budget"]) || "",
    max_budget: maxBudget,
    cuisine: String(data.cuisine ?? ""),
    min_rating: minRating === "0" ? "0" : minRating,
    additional_notes: String(data.additional_notes ?? ""),
  };
}

export function historyLabel(prefs: SearchPreferences): string {
  const parts = [prefs.location || "Anywhere"];
  if (prefs.budget === "custom" && prefs.max_budget) {
    parts.push(`Rs.${prefs.max_budget}`);
  } else if (prefs.budget) {
    parts.push(prefs.budget);
  }
  if (prefs.cuisine) {
    parts.push(prefs.cuisine);
  }
  return parts.join(" · ");
}
