export default function AnalyzeLoading() {
  return (
    <div
      className="py-12 bg-gray-50"
      role="status"
      aria-live="polite"
      aria-label="Loading quote form"
    >
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Heading skeleton */}
        <div className="text-center mb-8">
          <div className="h-10 w-72 bg-gray-200 rounded-lg mx-auto mb-4 animate-pulse" />
          <div className="h-5 w-96 max-w-full bg-gray-200 rounded mx-auto animate-pulse" />
        </div>

        {/* Form card skeleton */}
        <div className="card space-y-6 animate-pulse">
          {/* Project type field */}
          <div>
            <div className="h-4 w-28 bg-gray-200 rounded mb-2" />
            <div className="h-11 bg-gray-100 rounded-lg" />
          </div>
          {/* Location field */}
          <div>
            <div className="h-4 w-20 bg-gray-200 rounded mb-2" />
            <div className="h-11 bg-gray-100 rounded-lg" />
          </div>
          {/* Line items area */}
          <div>
            <div className="h-4 w-24 bg-gray-200 rounded mb-2" />
            <div className="h-32 bg-gray-100 rounded-lg" />
          </div>
          {/* Submit button */}
          <div className="h-12 w-48 bg-primary-200 rounded-lg mx-auto" />
        </div>
      </div>
      <span className="sr-only">Loading quote analysis form…</span>
    </div>
  );
}
