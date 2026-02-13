export default function GlobalLoading() {
  return (
    <div
      className="min-h-[60vh] flex items-center justify-center px-4 py-16"
      role="status"
      aria-live="polite"
      aria-label="Loading page"
    >
      <div className="text-center">
        <div className="relative w-12 h-12 mx-auto mb-4">
          <div className="absolute inset-0 rounded-full border-4 border-primary-200" />
          <div className="absolute inset-0 rounded-full border-4 border-primary-600 border-t-transparent animate-spin" />
        </div>
        <p className="text-gray-500 text-sm font-medium">Loading…</p>
      </div>
    </div>
  );
}
