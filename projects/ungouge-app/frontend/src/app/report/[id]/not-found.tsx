import Link from 'next/link';
import { FileX, FileText, Home } from 'lucide-react';

export default function ReportNotFound() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div
          className="card text-center py-12"
          role="alert"
          aria-live="polite"
        >
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gray-100 flex items-center justify-center">
            <FileX className="w-8 h-8 text-gray-500" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            Report Not Found
          </h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            We couldn&apos;t find this report. The link may be incorrect or the
            report may have expired. Try analyzing a new quote instead.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link
              href="/analyze"
              className="btn-primary inline-flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Analyze a Quote
            </Link>
            <Link
              href="/"
              className="btn-secondary inline-flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
