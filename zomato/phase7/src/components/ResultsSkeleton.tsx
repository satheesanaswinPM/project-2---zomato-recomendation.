export function ResultsSkeleton() {
  return (
    <section className="mt-10" aria-busy="true">
      <div className="mb-6 animate-pulse">
        <div className="h-8 w-56 rounded bg-white/60" />
        <div className="mt-2 h-4 w-72 rounded bg-white/50" />
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        {[1, 2, 3, 4].map((index) => (
          <div
            key={index}
            className="animate-pulse overflow-hidden rounded-2xl bg-white shadow-card"
          >
            <div className="h-36 bg-gray-200" />
            <div className="space-y-3 p-5">
              <div className="flex justify-between">
                <div className="h-6 w-40 rounded bg-gray-200" />
                <div className="h-6 w-12 rounded-md bg-gray-200" />
              </div>
              <div className="h-4 w-24 rounded bg-gray-200" />
              <div className="flex gap-2">
                <div className="h-6 w-16 rounded-full bg-gray-200" />
                <div className="h-6 w-20 rounded-full bg-gray-200" />
              </div>
              <div className="h-16 rounded-xl bg-gray-100" />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
