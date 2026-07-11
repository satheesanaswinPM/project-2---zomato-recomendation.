"use client";

import { useState } from "react";
import { SearchIcon } from "@/components/Icons";

interface NaturalLanguageSearchProps {
  loading: boolean;
  onParse: (query: string) => Promise<void>;
}

export function NaturalLanguageSearch({
  loading,
  onParse,
}: NaturalLanguageSearchProps) {
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!query.trim() || loading || busy) {
      return;
    }
    setBusy(true);
    try {
      await onParse(query.trim());
    } finally {
      setBusy(false);
    }
  }

  const disabled = loading || busy;

  return (
    <section className="mb-6 rounded-2xl border border-brand/15 bg-white/90 p-4 shadow-card backdrop-blur-sm sm:p-5 animate-fade-in">
      <h2 className="font-serif text-lg font-semibold text-ink-primary">
        Try natural language
      </h2>
      <p className="mt-1 text-sm text-ink-secondary">
        Example: &quot;Cheap Italian in Indiranagar, 4+ stars&quot;
      </p>
      <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          value={query}
          disabled={disabled}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you're craving..."
          className="w-full flex-1 rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-base text-ink-primary placeholder:text-gray-400"
        />
        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-brand px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-70 sm:min-w-[140px]"
        >
          {busy ? (
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          ) : (
            <SearchIcon className="h-4 w-4" />
          )}
          Fill form
        </button>
      </form>
    </section>
  );
}
