interface EmptyStateProps {
  message?: string | null;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="rounded-2xl bg-white/90 px-6 py-12 text-center shadow-card backdrop-blur-sm">
      <div
        className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 text-2xl text-gray-400"
        aria-hidden
      >
        &#128269;
      </div>
      <p className="font-serif text-xl font-semibold text-ink-primary">
        {message || "No restaurants found"}
      </p>
      <p className="mt-2 text-sm text-ink-secondary">
        Try lowering your minimum rating, changing cuisine, or adjusting budget.
      </p>
    </div>
  );
}
