"use client";

import type { SearchPreferences } from "@/lib/types";
import { BUDGET_OPTIONS, RATING_OPTIONS } from "@/lib/types";
import {
  ChevronDownIcon,
  MapPinIcon,
  SearchIcon,
  UtensilsIcon,
} from "@/components/Icons";

interface SearchFormProps {
  values: SearchPreferences;
  errors: Record<string, string>;
  loading: boolean;
  onChange: (values: SearchPreferences) => void;
  onSubmit: () => void;
}

function fieldClass(hasError: boolean): string {
  const base =
    "w-full rounded-lg border bg-white py-2.5 text-base text-ink-primary transition-colors";
  return hasError
    ? `${base} border-error pl-3`
    : `${base} border-gray-200 pl-10`;
}

function selectClass(hasError: boolean): string {
  const base =
    "w-full appearance-none rounded-lg border bg-white py-2.5 pl-3 pr-10 text-base text-ink-primary transition-colors";
  return hasError ? `${base} border-error` : `${base} border-gray-200`;
}

export function SearchForm({
  values,
  errors,
  loading,
  onChange,
  onSubmit,
}: SearchFormProps) {
  function update<K extends keyof SearchPreferences>(
    key: K,
    value: SearchPreferences[K],
  ) {
    onChange({ ...values, [key]: value });
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <section className="rounded-2xl bg-white/95 p-6 shadow-card backdrop-blur-sm sm:p-8">
      <h2 className="font-serif text-2xl font-semibold text-ink-primary">
        Your preferences
      </h2>
      <p className="mt-1 text-sm text-ink-secondary">
        Tell us what you&apos;re craving and we&apos;ll find the best spots.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5" noValidate>
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label
              htmlFor="location"
              className="mb-1.5 block text-sm font-medium text-ink-primary"
            >
              Location
            </label>
            <div className="relative">
              <MapPinIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                id="location"
                type="text"
                className={fieldClass(Boolean(errors.location))}
                placeholder="Bangalore"
                value={values.location}
                disabled={loading}
                onChange={(e) => update("location", e.target.value)}
              />
            </div>
            {errors.location && (
              <p className="mt-1.5 text-sm text-error">{errors.location}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="budget"
              className="mb-1.5 block text-sm font-medium text-ink-primary"
            >
              Budget (per person)
            </label>
            <div className="relative">
              <select
                id="budget"
                className={selectClass(Boolean(errors.budget))}
                value={values.budget}
                disabled={loading}
                onChange={(e) =>
                  update(
                    "budget",
                    e.target.value as SearchPreferences["budget"],
                  )
                }
              >
                <option value="" disabled>
                  Rs. 500 - 1,500
                </option>
                {BUDGET_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDownIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            </div>
            {errors.budget && (
              <p className="mt-1.5 text-sm text-error">{errors.budget}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="cuisine"
              className="mb-1.5 block text-sm font-medium text-ink-primary"
            >
              Cuisine
            </label>
            <div className="relative">
              <UtensilsIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                id="cuisine"
                type="text"
                className={fieldClass(false)}
                placeholder="e.g. North Indian, Pizza"
                value={values.cuisine}
                disabled={loading}
                onChange={(e) => update("cuisine", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="min_rating"
              className="mb-1.5 block text-sm font-medium text-ink-primary"
            >
              Minimum Rating
            </label>
            <div className="relative">
              <select
                id="min_rating"
                className={selectClass(Boolean(errors.min_rating))}
                value={values.min_rating}
                disabled={loading}
                onChange={(e) => update("min_rating", e.target.value)}
              >
                {RATING_OPTIONS.map((option) => (
                  <option key={option.value || "any"} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDownIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            </div>
            {errors.min_rating && (
              <p className="mt-1.5 text-sm text-error">{errors.min_rating}</p>
            )}
          </div>

          <div className="sm:col-span-2">
            <label
              htmlFor="additional_notes"
              className="mb-1.5 block text-sm font-medium text-ink-primary"
            >
              Additional notes <span className="font-normal text-ink-secondary">(optional)</span>
            </label>
            <textarea
              id="additional_notes"
              rows={2}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-base text-ink-primary transition-colors"
              placeholder="e.g. family-friendly, quick service"
              value={values.additional_notes}
              disabled={loading}
              onChange={(e) => update("additional_notes", e.target.value)}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-brand text-base font-semibold text-white shadow-sm transition-colors hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? (
            <span
              className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white"
              aria-hidden
            />
          ) : (
            <SearchIcon className="h-5 w-5" />
          )}
          {loading ? "Finding restaurants..." : "Find restaurants"}
        </button>
      </form>
    </section>
  );
}
