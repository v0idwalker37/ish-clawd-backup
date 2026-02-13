import Link from 'next/link';
import { Search, Home, FileText } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 py-16">
      <div className="text-center max-w-lg" role="alert" aria-live="polite">
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-primary-100 flex items-center justify-center">
          <Search className="w-10 h-10 text-primary-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Page Not Found
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          We couldn&apos;t find what you&apos;re looking for. It may have been moved
          or doesn&apos;t exist.
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link
            href="/"
            className="btn-primary inline-flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </Link>
          <Link
            href="/analyze"
            className="btn-secondary inline-flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            Analyze a Quote
          </Link>
        </div>
      </div>
    </div>
  );
}
