"use client";

import { useCallback, useState } from "react";
import { ApiError, fetchRecommendations } from "@/lib/api";
import type { DisplayPayload, SearchPreferences } from "@/lib/types";
import { EMPTY_PREFERENCES } from "@/lib/types";
import { SearchForm } from "@/components/SearchForm";
import { ResultsPanel } from "@/components/ResultsPanel";
import { ResultsSkeleton } from "@/components/ResultsSkeleton";
import { ErrorBanner } from "@/components/ErrorBanner";

export function RestaurantFinder() {
  const [preferences, setPreferences] =
    useState<SearchPreferences>(EMPTY_PREFERENCES);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [display, setDisplay] = useState<DisplayPayload | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = useCallback(async () => {
    setLoading(true);
    setFieldErrors({});
    setNetworkError(null);

    try {
      const response = await fetchRecommendations(preferences);

      if (!response.ok) {
        setDisplay(null);
        setFieldErrors(response.errors);
        return;
      }

      setDisplay(response.display);
    } catch (error) {
      setDisplay(null);
      if (error instanceof ApiError) {
        setNetworkError(error.message);
      } else {
        setNetworkError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, [preferences]);

  return (
    <main className="mx-auto min-h-screen max-w-content px-4 py-8 sm:py-10">
      <header className="mb-8">
        <h1 className="text-[1.75rem] font-semibold text-ink-primary sm:text-[2rem]">
          Restaurant Finder
        </h1>
        <p className="mt-1 text-ink-secondary">
          Enter your preferences and get personalized AI recommendations.
        </p>
      </header>

      <div className="space-y-6">
        <SearchForm
          values={preferences}
          errors={fieldErrors}
          loading={loading}
          onChange={setPreferences}
          onSubmit={handleSearch}
        />

        {networkError && (
          <ErrorBanner message={networkError} isError />
        )}

        {loading && <ResultsSkeleton />}

        {!loading && display && <ResultsPanel display={display} />}
      </div>

      <footer className="mt-10 text-center text-sm text-ink-secondary">
        Powered by AI · Data from Zomato dataset
      </footer>
    </main>
  );
}
