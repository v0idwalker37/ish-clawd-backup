'use client';

import { useEffect } from 'react';
import { AlertCircle, CreditCard, FileX, RefreshCw, Home, FileText } from 'lucide-react';
import Link from 'next/link';

type ErrorType = 'not-found' | 'payment-required' | 'server-error';

function classifyError(error: Error): ErrorType {
  const msg = error.message.toLowerCase();
  if (msg.includes('not found') || msg.includes('404')) return 'not-found';
  if (msg.includes('payment') || msg.includes('402') || msg.includes('unpaid'))
    return 'payment-required';
  return 'server-error';
}

const errorContent: Record<
  ErrorType,
  {
    icon: React.ReactNode;
    bgColor: string;
    title: string;
    description: string;
  }
> = {
  'not-found': {
    icon: <FileX className="w-7 h-7 text-gray-500" />,
    bgColor: 'bg-gray-100',
    title: 'Report Not Found',
    description:
      'This report doesn\'t exist or may have been removed. Double-check the link or analyze a new quote.',
  },
  'payment-required': {
    icon: <CreditCard className="w-7 h-7 text-amber-600" />,
    bgColor: 'bg-amber-100',
    title: 'Payment Required',
    description:
      'This report hasn\'t been paid for yet. Complete payment to view your full analysis.',
  },
  'server-error': {
    icon: <AlertCircle className="w-7 h-7 text-red-600" />,
    bgColor: 'bg-red-100',
    title: 'Error Loading Report',
    description:
      'We ran into a problem loading your report. This is usually temporary — please try again in a moment.',
  },
};

export default function ReportError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const errorType = classifyError(error);
  const content = errorContent[errorType];

  useEffect(() => {
    console.error('[ReportError]', { type: errorType, error });
  }, [error, errorType]);

  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div
          className="card text-center py-12"
          role="alert"
          aria-live="assertive"
        >
          <div
            className={`w-14 h-14 mx-auto mb-5 rounded-full ${content.bgColor} flex items-center justify-center`}
          >
            {content.icon}
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {content.title}
          </h1>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            {content.description}
          </p>
          {error.digest && (
            <p className="text-xs text-gray-400 mb-4 font-mono">
              Error ID: {error.digest}
            </p>
          )}
          <div className="flex items-center justify-center gap-4 flex-wrap">
            {errorType === 'server-error' && (
              <button
                onClick={reset}
                className="btn-primary inline-flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
            )}
            {errorType === 'payment-required' && (
              <button
                onClick={reset}
                className="bg-amber-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-amber-600 transition-colors inline-flex items-center gap-2"
              >
                <CreditCard className="w-4 h-4" />
                Complete Payment
              </button>
            )}
            <Link
              href="/analyze"
              className="btn-secondary inline-flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              New Analysis
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
