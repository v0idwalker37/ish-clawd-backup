import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Service Unavailable',
  robots: { index: false, follow: false },
};

export default function SunsetPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-xl w-full bg-white border border-gray-200 rounded-2xl shadow-sm p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-3">This service is currently unavailable.</h1>
        <p className="text-gray-600 mb-6">
          This service is not accepting new activity at this time.
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Please check back later.
        </p>
      </div>
    </div>
  );
}
