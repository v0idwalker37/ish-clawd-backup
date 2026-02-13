export default function ReportLoading() {
  return (
    <div
      className="py-12 bg-gray-50"
      role="status"
      aria-live="polite"
      aria-label="Loading report"
    >
      <div className="container mx-auto px-4 max-w-4xl animate-pulse">
        {/* Back link placeholder */}
        <div className="h-4 w-32 bg-gray-200 rounded mb-8" />

        {/* Header card */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="space-y-2">
              <div className="h-7 w-56 bg-gray-200 rounded" />
              <div className="h-4 w-40 bg-gray-100 rounded" />
            </div>
            <div className="h-10 w-36 bg-primary-200 rounded-lg" />
          </div>
        </div>

        {/* Price gauge / overview */}
        <div className="card mb-6">
          <div className="h-5 w-36 bg-gray-200 rounded mb-4" />
          <div className="flex items-center justify-center">
            <div className="w-48 h-48 rounded-full bg-gray-100 border-8 border-gray-200" />
          </div>
          <div className="grid grid-cols-3 gap-4 mt-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="text-center space-y-2">
                <div className="h-6 w-20 bg-gray-200 rounded mx-auto" />
                <div className="h-3 w-16 bg-gray-100 rounded mx-auto" />
              </div>
            ))}
          </div>
        </div>

        {/* Line items skeleton */}
        <div className="card">
          <div className="h-5 w-44 bg-gray-200 rounded mb-6" />
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="border border-gray-100 rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="h-5 w-40 bg-gray-200 rounded" />
                  <div className="h-5 w-20 bg-gray-200 rounded" />
                </div>
                <div className="h-3 w-full bg-gray-100 rounded" />
                <div className="h-3 w-3/4 bg-gray-100 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
      <span className="sr-only">Loading your quote analysis report…</span>
    </div>
  );
}
