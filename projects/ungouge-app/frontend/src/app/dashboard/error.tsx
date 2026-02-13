'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCw, Home, FileText } from 'lucide-react';
import Link from 'next/link';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[DashboardError]', error);
  }, [error]);

  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-6xl">
        <div
          className="card text-center py-12"
          role="alert"
          aria-live="assertive"
        >
          <div className="w-14 h-14 mx-auto mb-5 rounded-full bg-red-100 flex items-center justify-center">
            <AlertCircle className="w-7 h-7 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Dashboard Unavailable
          </h1>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            We couldn&apos;t load your dashboard right now. This is usually
            temporary — please try again.
          </p>
          {error.digest && (
            <p className="text-xs text-gray-400 mb-4 font-mono">
              Error ID: {error.digest}
            </p>
          )}
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={reset}
              className="btn-primary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
            <Link
              href="/analyze"
              className="btn-secondary inline-flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Analyze a Quote
            </Link>
            <Link
              href="/"
              className="text-gray-500 hover:text-gray-700 underline text-sm"
            >
              Go Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
