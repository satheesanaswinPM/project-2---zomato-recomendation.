"use client";

import { useCallback, useState } from "react";
import { ApiError, fetchRecommendations } from "@/lib/api";
import type { DisplayPayload, SearchPreferences } from "@/lib/types";
import { EMPTY_PREFERENCES } from "@/lib/types";
import { Header } from "@/components/Header";
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
  const [searchedLocation, setSearchedLocation] = useState("");

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

      setSearchedLocation(preferences.location);
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
    <div className="relative min-h-screen">
      <div
        className="pointer-events-none fixed inset-0 -z-10 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url(/images/food-background.png)" }}
        aria-hidden
      />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-white/75 backdrop-blur-[2px]" aria-hidden />

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <Header />

        <SearchForm
          values={preferences}
          errors={fieldErrors}
          loading={loading}
          onChange={setPreferences}
          onSubmit={handleSearch}
        />

        {networkError && (
          <div className="mt-6">
            <ErrorBanner message={networkError} isError />
          </div>
        )}

        {loading && <ResultsSkeleton />}

        {!loading && display && (
          <ResultsPanel display={display} location={searchedLocation} />
        )}

        <footer className="mt-12 pb-6 text-center text-sm text-ink-secondary">
          Powered by AI · Data from Zomato dataset
        </footer>
      </main>
    </div>
  );
}
