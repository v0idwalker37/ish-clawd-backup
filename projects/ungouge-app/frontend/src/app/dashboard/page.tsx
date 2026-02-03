'use client';

import Link from 'next/link';
import { FileText, DollarSign, TrendingDown, Clock, ArrowRight, CheckCircle, AlertTriangle } from 'lucide-react';

export default function DashboardPage() {
  // Mock data - in a real app, this would come from an API
  const stats = {
    totalReports: 12,
    totalSavings: 8450,
    averageSavings: 704,
    pendingReports: 2,
  };

  // Demo mode - set to empty array to show empty state
  type Quote = {
    id: string;
    projectType: string;
    contractor: string;
    quoteAmount: number;
    fairPrice: number;
    savings: number;
    status: string;
    date: string;
    overallRating: string;
  };

  const recentQuotes: Quote[] = [
    // Uncomment for demo data
    // {
    //   id: 'QT-2024-001',
    //   projectType: 'Kitchen Remodel',
    //   contractor: 'ABC Renovations',
    //   quoteAmount: 45000,
    //   fairPrice: 38500,
    //   savings: 6500,
    //   status: 'completed',
    //   date: '2024-02-01',
    //   overallRating: 'gouged',
    // },
  ];

  const getStatusBadge = (status: string) => {
    if (status === 'completed') {
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
          <CheckCircle className="w-3 h-3" />
          Completed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
        <Clock className="w-3 h-3" />
        Processing
      </span>
    );
  };

  const getRatingBadge = (rating: string) => {
    const configs = {
      gouged: { color: 'bg-red-100 text-red-700', label: 'Overpriced', icon: AlertTriangle },
      fair: { color: 'bg-blue-100 text-blue-700', label: 'Fair Price', icon: CheckCircle },
      good: { color: 'bg-green-100 text-green-700', label: 'Good Deal', icon: CheckCircle },
    };
    const config = configs[rating as keyof typeof configs] || configs.fair;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Track your quote analyses and savings</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total Reports</p>
            <FileText className="w-5 h-5 text-primary-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.totalReports}</p>
          <p className="text-xs text-gray-500 mt-1">Lifetime analyses</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total Savings</p>
            <DollarSign className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600">
            ${stats.totalSavings.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 mt-1">Identified overcharges</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Avg Savings</p>
            <TrendingDown className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-600">
            ${stats.averageSavings.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 mt-1">Per quote analyzed</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Pending</p>
            <Clock className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-yellow-600">{stats.pendingReports}</p>
          <p className="text-xs text-gray-500 mt-1">Being processed</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            href="/analyze"
            className="flex items-center justify-between p-4 border-2 border-primary-200 rounded-lg hover:border-primary-600 hover:bg-primary-50 transition-all group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-white">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">New Analysis</p>
                <p className="text-sm text-gray-600">Upload a contractor quote</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-primary-600 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            href="/dashboard/quotes"
            className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center text-white">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">View All Quotes</p>
                <p className="text-sm text-gray-600">Browse your history</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-600 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>

      {/* Recent Quotes */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Recent Quotes</h2>
          <Link href="/dashboard/quotes" className="text-primary-600 hover:text-primary-700 text-sm font-semibold">
            View All →
          </Link>
        </div>

        <div className="space-y-4">
          {recentQuotes.length === 0 ? (
            // Empty State
            <div className="text-center py-16 px-4">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">No quotes yet</h3>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Get started by uploading your first contractor quote to see how much you could save!
              </p>
              <Link
                href="/analyze"
                className="inline-flex items-center gap-2 bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 hover:shadow-lg active:scale-95 transition-all"
              >
                <FileText className="w-5 h-5" />
                Analyze Your First Quote
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          ) : (
            recentQuotes.map((quote) => {
              const { overallRating, status, id, projectType, contractor, quoteAmount, fairPrice, savings, date } = quote;
              return (
            <div key={id} className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{projectType}</h3>
                    {getRatingBadge(overallRating)}
                  </div>
                  <p className="text-sm text-gray-600">
                    {contractor} • {id}
                  </p>
                </div>
                {getStatusBadge(status)}
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 text-sm">
                <div>
                  <p className="text-gray-500 mb-1">Quote Amount</p>
                  <p className="font-semibold text-gray-900">
                    ${quoteAmount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Fair Price</p>
                  <p className="font-semibold text-gray-900">
                    ${fairPrice.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Potential Savings</p>
                  <p className={`font-semibold ${savings > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {savings > 0 ? '+' : ''}${Math.abs(savings).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Date</p>
                  <p className="font-semibold text-gray-900">
                    {new Date(date).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {status === 'completed' && (
                <div className="mt-3 pt-3 border-t">
                  <Link
                    href={`/report/${id}`}
                    className="text-primary-600 hover:text-primary-700 text-sm font-semibold flex items-center gap-1"
                  >
                    View Full Report
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              )}
            </div>
              );
            })
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-200">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center text-white flex-shrink-0">
            <FileText className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Need help understanding your reports?
            </h3>
            <p className="text-gray-600 mb-4">
              Our team is here to help you interpret your quote analysis and negotiate with contractors effectively.
            </p>
            <Link
              href="/support"
              className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-semibold"
            >
              Contact Support
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
