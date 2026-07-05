import type { DisplayRecommendation } from "@/lib/types";
import { MapPinIcon, UtensilsIcon, WalletIcon } from "@/components/Icons";

interface RecommendationCardProps {
  item: DisplayRecommendation;
}

function splitCuisine(cuisine: string): string[] {
  if (!cuisine || cuisine === "Cuisine not listed") {
    return [];
  }
  return cuisine
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function formatCost(costLabel: string): string {
  if (!costLabel || costLabel === "Price not available") {
    return "Price not available";
  }
  if (costLabel.toLowerCase().includes("for two")) {
    return costLabel;
  }
  return `${costLabel} for two`;
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  const cuisines = splitCuisine(item.cuisine);
  const rating =
    item.rating_label === "Unrated" ? null : item.rating_label;

  return (
    <article className="relative overflow-hidden rounded-2xl bg-white shadow-card transition-shadow hover:shadow-lg">
      <div className="absolute left-3 top-3 z-10 rounded-md bg-brand px-2 py-0.5 text-xs font-bold text-white">
        #{item.rank}
      </div>

      <div className="flex h-36 items-center justify-center bg-gradient-to-br from-gray-100 to-gray-50">
        <UtensilsIcon className="h-10 w-10 text-gray-300" />
      </div>

      <div className="p-4 sm:p-5">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-serif text-xl font-semibold leading-tight text-ink-primary">
            {item.name}
          </h3>
          {rating && (
            <span className="inline-flex shrink-0 items-center gap-1 rounded-md bg-rating px-2 py-1 text-xs font-semibold text-white">
              {rating}
              <span aria-hidden>★</span>
            </span>
          )}
        </div>

        <div className="mt-2 flex items-center gap-1.5 text-sm text-ink-secondary">
          <MapPinIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
          <span>{item.location}</span>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          {cuisines.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-gray-100 px-2.5 py-1 text-xs text-ink-secondary"
            >
              {tag}
            </span>
          ))}
          <span className="inline-flex items-center gap-1 text-xs text-ink-secondary">
            <WalletIcon className="text-gray-400" />
            {formatCost(item.cost_label)}
          </span>
        </div>

        <div className="mt-4 rounded-xl bg-surface-muted px-4 py-3 text-sm leading-relaxed text-ink-primary">
          <span className="font-semibold">AI Match: </span>
          {item.explanation}
        </div>
      </div>
    </article>
  );
}
