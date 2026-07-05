import type { DisplayRecommendation } from "@/lib/types";

interface RecommendationCardProps {
  item: DisplayRecommendation;
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  return (
    <article className="rounded-[10px] border border-gray-200 bg-surface-muted p-4 transition-shadow hover:shadow-card sm:p-5">
      <div className="mb-1 text-sm font-bold text-brand">#{item.rank}</div>
      <h3 className="mb-2 text-lg font-semibold text-ink-primary">{item.name}</h3>

      <div className="mb-3 flex flex-wrap gap-2">
        <MetaChip label={item.location} />
        <MetaChip label={item.cuisine} />
        <MetaChip label={item.cost_label} />
        <MetaChip label={`Rating ${item.rating_label}`} />
      </div>

      <p className="text-[0.95rem] leading-relaxed text-ink-primary">
        <span className="font-semibold">Why: </span>
        {item.explanation}
      </p>
    </article>
  );
}

function MetaChip({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-white px-2.5 py-1 text-xs text-ink-secondary ring-1 ring-gray-200">
      {label}
    </span>
  );
}
