"use client";

import type { SearchHistoryItem } from "@/lib/types";

interface SearchHistoryProps {
  items: SearchHistoryItem[];
  onSelect: (item: SearchHistoryItem) => void;
  onClear: () => void;
}

export function SearchHistory({ items, onSelect, onClear }: SearchHistoryProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className="mb-6 rounded-2xl bg-white/80 p-4 shadow-card backdrop-blur-sm animate-fade-in">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="font-serif text-lg font-semibold text-ink-primary">
          Recent searches
        </h2>
        <button
          type="button"
          onClick={onClear}
          className="text-xs font-medium text-ink-secondary hover:text-brand"
        >
          Clear
        </button>
      </div>
      <ul className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
        {items.map((item) => (
          <li key={`${item.label}-${item.created_at}`}>
            <button
              type="button"
              onClick={() => onSelect(item)}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-left text-sm text-ink-primary transition-colors hover:border-brand hover:text-brand sm:w-auto"
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
