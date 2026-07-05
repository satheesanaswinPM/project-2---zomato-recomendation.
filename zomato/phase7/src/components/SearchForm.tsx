"use client";

import type { SearchPreferences } from "@/lib/types";
import { BUDGET_OPTIONS } from "@/lib/types";

interface SearchFormProps {
  values: SearchPreferences;
  errors: Record<string, string>;
  loading: boolean;
  onChange: (values: SearchPreferences) => void;
  onSubmit: () => void;
}

function fieldClass(hasError: boolean): string {
  const base =
    "w-full rounded-lg border px-3 py-2.5 text-base text-ink-primary transition-colors";
  return hasError
    ? `${base} border-error focus:border-error`
    : `${base} border-gray-300`;
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
    <section className="rounded-xl bg-surface-card p-6 shadow-card">
      <h2 className="mb-5 text-lg font-semibold text-ink-primary">
        Your preferences
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <div className="grid gap-5 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label
              htmlFor="location"
              className="mb-1.5 block text-sm font-semibold text-ink-primary"
            >
              Location *
            </label>
            <input
              id="location"
              type="text"
              className={fieldClass(Boolean(errors.location))}
              placeholder="e.g. Marathahalli, Bangalore"
              value={values.location}
              disabled={loading}
              onChange={(e) => update("location", e.target.value)}
            />
            {errors.location && (
              <p className="mt-1.5 text-sm text-error">{errors.location}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="budget"
              className="mb-1.5 block text-sm font-semibold text-ink-primary"
            >
              Budget *
            </label>
            <select
              id="budget"
              className={fieldClass(Boolean(errors.budget))}
              value={values.budget}
              disabled={loading}
              onChange={(e) =>
                update("budget", e.target.value as SearchPreferences["budget"])
              }
            >
              <option value="" disabled>
                Select budget
              </option>
              {BUDGET_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.budget && (
              <p className="mt-1.5 text-sm text-error">{errors.budget}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="cuisine"
              className="mb-1.5 block text-sm font-semibold text-ink-primary"
            >
              Cuisine
            </label>
            <input
              id="cuisine"
              type="text"
              className={fieldClass(false)}
              placeholder="e.g. Italian, North Indian"
              value={values.cuisine}
              disabled={loading}
              onChange={(e) => update("cuisine", e.target.value)}
            />
          </div>

          <div>
            <label
              htmlFor="min_rating"
              className="mb-1.5 block text-sm font-semibold text-ink-primary"
            >
              Minimum rating
            </label>
            <input
              id="min_rating"
              type="number"
              min={0}
              max={5}
              step={0.1}
              className={fieldClass(Boolean(errors.min_rating))}
              placeholder="0 - 5"
              value={values.min_rating}
              disabled={loading}
              onChange={(e) => update("min_rating", e.target.value)}
            />
            {errors.min_rating && (
              <p className="mt-1.5 text-sm text-error">{errors.min_rating}</p>
            )}
          </div>

          <div className="sm:col-span-2">
            <label
              htmlFor="additional_notes"
              className="mb-1.5 block text-sm font-semibold text-ink-primary"
            >
              Additional notes
            </label>
            <textarea
              id="additional_notes"
              rows={3}
              className={fieldClass(false)}
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
          className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-brand text-base font-semibold text-white transition-colors hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-70 sm:w-auto sm:min-w-[200px] sm:px-8"
        >
          {loading && (
            <span
              className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white"
              aria-hidden
            />
          )}
          {loading ? "Finding restaurants..." : "Find restaurants"}
        </button>

        {loading && (
          <p className="text-sm text-ink-secondary">
            Analyzing restaurants with AI — this may take a few seconds.
          </p>
        )}
      </form>
    </section>
  );
}
