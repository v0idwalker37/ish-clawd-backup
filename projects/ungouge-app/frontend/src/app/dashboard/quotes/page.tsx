'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FileText, Clock, CheckCircle, AlertTriangle, ArrowRight, Search } from 'lucide-react';
import api from '@/lib/api';

interface Quote {
  id: string;
  project_type: string;
  description: string;
  status: string;
  created_at: string;
  total_amount?: number;
}

export default function QuotesPage() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        const data = await api.get('/api/quotes');
        setQuotes(data.quotes || []);
      } catch (error) {
        console.error('Failed to fetch quotes:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuotes();
  }, []);

  const getStatusBadge = (status: string) => {
    const configs: Record<string, { color: string; icon: typeof CheckCircle; label: string }> = {
      completed: { color: 'bg-green-100 text-green-700', icon: CheckCircle, label: 'Completed' },
      processing: { color: 'bg-yellow-100 text-yellow-700', icon: Clock, label: 'Processing' },
      pending: { color: 'bg-blue-100 text-blue-700', icon: Clock, label: 'Pending' },
    };
    const config = configs[status] || configs.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  const filteredQuotes = quotes.filter(
    (quote) =>
      quote.project_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      quote.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading quotes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Quotes</h1>
          <p className="text-gray-600 mt-1">View and manage all your quote analyses</p>
        </div>
        <Link
          href="/analyze"
          className="btn-primary inline-flex items-center gap-2 self-start"
        >
          <FileText className="w-5 h-5" />
          New Analysis
        </Link>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search quotes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      {/* Quotes List */}
      {filteredQuotes.length === 0 ? (
        <div className="card text-center py-16">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <FileText className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">
            {quotes.length === 0 ? 'No quotes yet' : 'No matching quotes'}
          </h3>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            {quotes.length === 0
              ? 'Get started by uploading your first contractor quote!'
              : 'Try adjusting your search terms'}
          </p>
          {quotes.length === 0 && (
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 btn-primary"
            >
              <FileText className="w-5 h-5" />
              Analyze Your First Quote
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredQuotes.map((quote) => (
            <div
              key={quote.id}
              className="card hover:border-primary-300 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900">{quote.project_type || 'Quote'}</h3>
                    {getStatusBadge(quote.status)}
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {quote.description || 'No description provided'}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    Submitted {new Date(quote.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  {quote.total_amount && (
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Quote Amount</p>
                      <p className="font-semibold text-gray-900">
                        ${quote.total_amount.toLocaleString()}
                      </p>
                    </div>
                  )}
                  <Link
                    href={`/report/${quote.id}`}
                    className="text-primary-600 hover:text-primary-700 font-semibold flex items-center gap-1"
                  >
                    View
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
