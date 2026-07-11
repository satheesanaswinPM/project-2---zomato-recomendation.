"use client";

import { useState } from "react";

interface FollowUpBarProps {
  loading: boolean;
  onRefine: (followUp: string) => Promise<void>;
}

const SUGGESTIONS = [
  "Show me cheaper options",
  "Only outdoor seating",
  "Higher rating please",
];

export function FollowUpBar({ loading, onRefine }: FollowUpBarProps) {
  const [followUp, setFollowUp] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(text: string) {
    const value = text.trim();
    if (!value || loading || busy) {
      return;
    }
    setBusy(true);
    try {
      await onRefine(value);
      setFollowUp("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mt-6 rounded-2xl bg-white/95 p-4 shadow-card animate-fade-in sm:p-5">
      <h3 className="font-serif text-lg font-semibold text-ink-primary">
        Refine results
      </h3>
      <p className="mt-1 text-sm text-ink-secondary">
        Keep the conversation going without restarting your search.
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((item) => (
          <button
            key={item}
            type="button"
            disabled={loading || busy}
            onClick={() => run(item)}
            className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-xs text-ink-secondary transition-colors hover:border-brand hover:text-brand disabled:opacity-60"
          >
            {item}
          </button>
        ))}
      </div>

      <form
        className="mt-3 flex flex-col gap-2 sm:flex-row"
        onSubmit={(e) => {
          e.preventDefault();
          void run(followUp);
        }}
      >
        <input
          type="text"
          value={followUp}
          disabled={loading || busy}
          onChange={(e) => setFollowUp(e.target.value)}
          placeholder="e.g. Show me cheaper options"
          className="w-full flex-1 rounded-lg border border-gray-200 px-3 py-2.5 text-base placeholder:text-gray-400"
        />
        <button
          type="submit"
          disabled={loading || busy || !followUp.trim()}
          className="h-11 rounded-xl bg-ink-primary px-4 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-60 sm:min-w-[120px]"
        >
          {busy ? "Updating..." : "Apply"}
        </button>
      </form>
    </section>
  );
}
