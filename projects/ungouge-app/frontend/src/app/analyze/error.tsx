'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';

export default function AnalyzeError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[AnalyzeError]', error);
  }, [error]);

  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div
          className="card text-center py-12"
          role="alert"
          aria-live="assertive"
        >
          <div className="w-14 h-14 mx-auto mb-5 rounded-full bg-red-100 flex items-center justify-center">
            <AlertCircle className="w-7 h-7 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Couldn&apos;t Load the Quote Form
          </h1>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Something went wrong loading the analysis form. This is usually
            temporary — please try again.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={reset}
              className="btn-primary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
            <Link
              href="/"
              className="btn-secondary inline-flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
