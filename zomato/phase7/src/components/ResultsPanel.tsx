import type { DisplayPayload } from "@/lib/types";
import { RecommendationCard } from "@/components/RecommendationCard";
import { EmptyState } from "@/components/EmptyState";
import { ErrorBanner } from "@/components/ErrorBanner";

interface ResultsPanelProps {
  display: DisplayPayload;
  location?: string;
}

export function ResultsPanel({ display, location }: ResultsPanelProps) {
  const area = location?.trim() || "your area";

  return (
    <section className="mt-10">
      <div className="mb-6">
        <h2 className="font-serif text-2xl font-semibold text-ink-primary">
          {display.title}
        </h2>
        <p className="mt-1 text-sm text-ink-secondary">
          Top matches based on your preferences in {area}.
        </p>
        {display.summary && (
          <p className="mt-2 text-sm text-ink-secondary/80">{display.summary}</p>
        )}
      </div>

      {display.message && (
        <ErrorBanner message={display.message} isError={display.is_error} />
      )}

      {display.warnings.map((warning) => (
        <div
          key={warning}
          className="mb-4 rounded-lg border border-notice-warn-border bg-notice-warn-bg px-4 py-2 text-sm text-notice-warn-text"
        >
          {warning}
        </div>
      ))}

      {display.is_empty ? (
        <EmptyState message={display.message} />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2">
          {display.recommendations.map((item) => (
            <RecommendationCard key={`${item.rank}-${item.name}`} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}
