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
          We are performing a transition and this site is not accepting new activity.
        </p>
        <a
          href="https://gougealert.com"
          className="inline-block bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
        >
          Continue to GougeAlert.com
        </a>
        <p className="text-xs text-gray-500 mt-6">
          If you need help, contact: support@gougealert.com
        </p>
      </div>
    </div>
  );
}
