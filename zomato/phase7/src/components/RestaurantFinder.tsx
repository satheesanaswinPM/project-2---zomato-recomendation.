"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  clearLocalHistory,
  fetchRecommendations,
  loadLocalHistory,
  parseNaturalLanguage,
  pushLocalHistory,
  refineSearch,
} from "@/lib/api";
import type {
  DisplayPayload,
  SearchHistoryItem,
  SearchPreferences,
} from "@/lib/types";
import { EMPTY_PREFERENCES, preferencesFromApi } from "@/lib/types";
import { Header } from "@/components/Header";
import { SearchForm } from "@/components/SearchForm";
import { ResultsPanel } from "@/components/ResultsPanel";
import { ResultsSkeleton } from "@/components/ResultsSkeleton";
import { ErrorBanner } from "@/components/ErrorBanner";
import { NaturalLanguageSearch } from "@/components/NaturalLanguageSearch";
import { FollowUpBar } from "@/components/FollowUpBar";
import { SearchHistory } from "@/components/SearchHistory";

export function RestaurantFinder() {
  const [preferences, setPreferences] =
    useState<SearchPreferences>(EMPTY_PREFERENCES);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [display, setDisplay] = useState<DisplayPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchedLocation, setSearchedLocation] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);

  useEffect(() => {
    setHistory(loadLocalHistory());
  }, []);

  const handleSearch = useCallback(async () => {
    setLoading(true);
    setFieldErrors({});
    setNetworkError(null);

    try {
      const response = await fetchRecommendations(preferences, {
        sessionId,
      });

      if (!response.ok) {
        setDisplay(null);
        setFieldErrors(response.errors);
        return;
      }

      setSearchedLocation(preferences.location);
      setDisplay(response.display);
      setSessionId(response.session_id ?? null);
      setCacheHit(Boolean(response.cache_hit));
      setHistory((prev) => pushLocalHistory(preferences, prev));
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
  }, [preferences, sessionId]);

  const handleParseNl = useCallback(async (query: string) => {
    setNetworkError(null);
    setFieldErrors({});
    try {
      const parsed = await parseNaturalLanguage(query);
      if (!parsed.ok || !parsed.preferences) {
        setNetworkError(
          parsed.message ||
            Object.values(parsed.errors || {})[0] ||
            "Could not understand that request.",
        );
        return;
      }
      setPreferences(preferencesFromApi(parsed.preferences));
    } catch (error) {
      if (error instanceof ApiError) {
        setNetworkError(error.message);
      } else {
        setNetworkError("Natural language parsing failed.");
      }
    }
  }, []);

  const handleRefine = useCallback(
    async (followUp: string) => {
      if (!sessionId) {
        setNetworkError("Run a search first, then refine the results.");
        return;
      }
      setLoading(true);
      setNetworkError(null);
      try {
        const refined = await refineSearch(sessionId, followUp);
        if (!refined.ok || !refined.display) {
          setNetworkError(
            refined.message ||
              Object.values(refined.errors || {})[0] ||
              "Could not refine results.",
          );
          return;
        }
        if (refined.preferences) {
          setPreferences(preferencesFromApi(refined.preferences));
        }
        setDisplay(refined.display);
        setSessionId(refined.session_id ?? sessionId);
        setCacheHit(Boolean(refined.cache_hit));
        setSearchedLocation(
          String(refined.preferences?.location || searchedLocation),
        );
      } catch (error) {
        if (error instanceof ApiError) {
          setNetworkError(error.message);
        } else {
          setNetworkError("Follow-up refinement failed.");
        }
      } finally {
        setLoading(false);
      }
    },
    [sessionId, searchedLocation],
  );

  return (
    <div className="relative min-h-screen">
      <div
        className="pointer-events-none fixed inset-0 -z-10 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url(/images/food-background.png)" }}
        aria-hidden
      />
      <div
        className="pointer-events-none fixed inset-0 -z-10 bg-white/75 backdrop-blur-[2px]"
        aria-hidden
      />

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <Header />

        <NaturalLanguageSearch loading={loading} onParse={handleParseNl} />

        <SearchHistory
          items={history}
          onSelect={(item) => {
            setPreferences(item.preferences);
            setFieldErrors({});
            setNetworkError(null);
          }}
          onClear={() => {
            clearLocalHistory();
            setHistory([]);
          }}
        />

        <SearchForm
          values={preferences}
          errors={fieldErrors}
          loading={loading}
          onChange={setPreferences}
          onSubmit={handleSearch}
        />

        {networkError && (
          <div className="mt-6 animate-fade-in">
            <ErrorBanner message={networkError} isError />
          </div>
        )}

        {cacheHit && !loading && display && (
          <p className="mt-4 text-center text-xs text-ink-secondary animate-fade-in">
            Served from recent search cache
          </p>
        )}

        {loading && <ResultsSkeleton />}

        {!loading && display && (
          <>
            <div className="animate-fade-in">
              <ResultsPanel display={display} location={searchedLocation} />
            </div>
            <FollowUpBar loading={loading} onRefine={handleRefine} />
          </>
        )}

        <footer className="mt-12 pb-6 text-center text-sm text-ink-secondary">
          Powered by AI · Data from Zomato dataset
        </footer>
      </main>
    </div>
  );
}
