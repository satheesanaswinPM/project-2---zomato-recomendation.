interface EmptyStateProps {
  message?: string | null;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="py-8 text-center text-ink-secondary">
      <div
        className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 text-2xl text-gray-400"
        aria-hidden
      >
        &#128269;
      </div>
      <p className="text-lg font-medium text-ink-primary">
        {message || "No restaurants found"}
      </p>
      <p className="mt-2 text-sm">
        Try lowering your minimum rating, changing cuisine, or adjusting budget.
      </p>
    </div>
  );
}
