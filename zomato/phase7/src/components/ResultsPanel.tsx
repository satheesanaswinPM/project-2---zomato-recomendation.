import type { DisplayPayload } from "@/lib/types";
import { RecommendationCard } from "@/components/RecommendationCard";
import { EmptyState } from "@/components/EmptyState";
import { ErrorBanner } from "@/components/ErrorBanner";

interface ResultsPanelProps {
  display: DisplayPayload;
}

export function ResultsPanel({ display }: ResultsPanelProps) {
  return (
    <section className="rounded-xl bg-surface-card p-6 shadow-card">
      <h2 className="mb-4 text-lg font-semibold text-ink-primary">
        {display.title}
      </h2>

      {display.summary && (
        <p className="mb-4 text-[1.05rem] text-ink-secondary">{display.summary}</p>
      )}

      {display.message && (
        <ErrorBanner message={display.message} isError={display.is_error} />
      )}

      {display.warnings.map((warning) => (
        <div
          key={warning}
          className="mb-3 rounded-lg border border-notice-warn-border bg-notice-warn-bg px-4 py-2 text-sm text-notice-warn-text"
        >
          {warning}
        </div>
      ))}

      {display.is_empty ? (
        <EmptyState message={display.message} />
      ) : (
        <div className="flex flex-col gap-4">
          {display.recommendations.map((item) => (
            <RecommendationCard key={`${item.rank}-${item.name}`} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}
