export type BudgetLevel = "low" | "medium" | "high";

export interface SearchPreferences {
  location: string;
  budget: BudgetLevel | "";
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
}

export interface ErrorResponse {
  ok: false;
  errors: Record<string, string>;
}

export type RecommendationsResponse = SuccessResponse | ErrorResponse;

export const EMPTY_PREFERENCES: SearchPreferences = {
  location: "",
  budget: "",
  cuisine: "",
  min_rating: "",
  additional_notes: "",
};

export const BUDGET_OPTIONS: { value: BudgetLevel; label: string }[] = [
  { value: "low", label: "Rs. 0 - 500" },
  { value: "medium", label: "Rs. 500 - 1,500" },
  { value: "high", label: "Rs. 1,501+" },
];

export const RATING_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "Any rating" },
  { value: "3.5", label: "3.5+" },
  { value: "4", label: "4.0+" },
  { value: "4.5", label: "4.5+" },
];
