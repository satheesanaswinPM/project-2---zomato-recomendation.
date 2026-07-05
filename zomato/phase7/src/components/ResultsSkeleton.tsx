export function ResultsSkeleton() {
  return (
    <section className="rounded-xl bg-surface-card p-6 shadow-card" aria-busy="true">
      <h2 className="mb-4 text-lg font-semibold text-ink-primary">
        Your Recommendations
      </h2>
      <div className="flex flex-col gap-4">
        {[1, 2, 3].map((index) => (
          <div
            key={index}
            className="animate-pulse rounded-[10px] border border-gray-200 bg-surface-muted p-5"
          >
            <div className="mb-3 h-4 w-8 rounded bg-gray-200" />
            <div className="mb-3 h-6 w-48 rounded bg-gray-200" />
            <div className="mb-4 flex flex-wrap gap-2">
              <div className="h-6 w-20 rounded-full bg-gray-200" />
              <div className="h-6 w-28 rounded-full bg-gray-200" />
              <div className="h-6 w-16 rounded-full bg-gray-200" />
            </div>
            <div className="space-y-2">
              <div className="h-3 w-full rounded bg-gray-200" />
              <div className="h-3 w-[80%] rounded bg-gray-200" />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
