export default function DashboardLoading() {
  return (
    <div
      className="py-12 bg-gray-50"
      role="status"
      aria-live="polite"
      aria-label="Loading dashboard"
    >
      <div className="container mx-auto px-4 max-w-6xl animate-pulse">
        {/* Heading */}
        <div className="h-9 w-48 bg-gray-200 rounded mb-8" />

        {/* Stats row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card space-y-3">
              <div className="h-4 w-24 bg-gray-200 rounded" />
              <div className="h-8 w-20 bg-gray-100 rounded" />
            </div>
          ))}
        </div>

        {/* Recent quotes table skeleton */}
        <div className="card">
          <div className="h-6 w-40 bg-gray-200 rounded mb-6" />
          <div className="space-y-4">
            {/* Table header */}
            <div className="grid grid-cols-5 gap-4 pb-3 border-b border-gray-100">
              {['w-20', 'w-28', 'w-24', 'w-16', 'w-20'].map((w, i) => (
                <div
                  key={i}
                  className={`h-3 ${w} bg-gray-200 rounded`}
                />
              ))}
            </div>
            {/* Table rows */}
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="grid grid-cols-5 gap-4 py-3 border-b border-gray-50"
              >
                <div className="h-4 w-28 bg-gray-100 rounded" />
                <div className="h-4 w-32 bg-gray-100 rounded" />
                <div className="h-4 w-20 bg-gray-100 rounded" />
                <div className="h-4 w-16 bg-gray-100 rounded" />
                <div className="h-4 w-20 bg-gray-100 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
      <span className="sr-only">Loading your dashboard…</span>
    </div>
  );
}
