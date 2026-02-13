'use client';

import QuoteForm from '@/components/QuoteForm';

export default function AnalyzePageContent() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Analyze Your Quote</h1>
          <p className="text-xl text-gray-600">
            Enter your contractor quote details to get instant analysis.
          </p>
        </div>
        <QuoteForm />
      </div>
    </div>
  );
}
