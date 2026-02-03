'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import ReportCard from '@/components/ReportCard';
import PriceGauge from '@/components/PriceGauge';
import { ArrowLeft, Download, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface LineItemAnalysis {
  item_name: string;
  quoted_price: number;
  fair_price_low: number;
  fair_price_high: number;
  assessment: 'fair' | 'slightly_high' | 'high' | 'gouging';
  explanation: string;
  bls_rate?: number;
  material_cost?: number;
}

interface Report {
  id: string;
  project_type: string;
  location: string;
  total_quoted: number;
  total_fair_low: number;
  total_fair_high: number;
  overall_assessment: string;
  line_items: LineItemAnalysis[];
  created_at: string;
}

export default function ReportPage() {
  const params = useParams();
  const reportId = params.id as string;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`);
        setReport(response.data);
      } catch (err) {
        setError('Failed to load report. Please check your report ID.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [reportId]);

  if (loading) {
    return (
      <div className="py-20 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="py-20">
        <div className="container mx-auto px-4 max-w-2xl">
          <div className="card text-center">
            <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" />
            <h1 className="text-2xl font-bold mb-4">Report Not Found</h1>
            <p className="text-gray-600 mb-6">{error || 'The report you\'re looking for doesn\'t exist.'}</p>
            <Link href="/analyze" className="btn-primary">
              Analyze a New Quote
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const savingsPotential = report.total_quoted - report.total_fair_high;

  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-6xl">
        <Link href="/" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Link>

        {/* Header */}
        <div className="card mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">Quote Analysis Report</h1>
              <p className="text-gray-600">
                {report.project_type} • {report.location}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Generated: {new Date(report.created_at).toLocaleDateString()}
              </p>
            </div>
            <button className="btn-secondary flex items-center">
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </button>
          </div>

          {/* Overall Summary */}
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Quoted</p>
              <p className="text-3xl font-bold">${report.total_quoted.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Fair Price Range</p>
              <p className="text-3xl font-bold text-success">
                ${report.total_fair_low.toLocaleString()} - ${report.total_fair_high.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Potential Savings</p>
              <p className={`text-3xl font-bold ${savingsPotential > 0 ? 'text-danger' : 'text-success'}`}>
                {savingsPotential > 0 ? `$${savingsPotential.toLocaleString()}` : '$0'}
              </p>
            </div>
          </div>

          {/* Overall Gauge */}
          <PriceGauge
            quotedPrice={report.total_quoted}
            fairLow={report.total_fair_low}
            fairHigh={report.total_fair_high}
          />

          <div className="mt-6 p-4 bg-primary-50 rounded-lg">
            <p className="font-semibold text-primary-900 mb-2">Overall Assessment:</p>
            <p className="text-gray-700">{report.overall_assessment}</p>
          </div>
        </div>

        {/* Line Items */}
        <h2 className="text-2xl font-bold mb-6">Line Item Breakdown</h2>
        <div className="space-y-6">
          {report.line_items.map((item, index) => (
            <ReportCard key={index} lineItem={item} />
          ))}
        </div>

        {/* Actions */}
        <div className="mt-12 card text-center">
          <h3 className="text-2xl font-bold mb-4">What's Next?</h3>
          <p className="text-gray-600 mb-6">
            Use this report to negotiate with your contractor or get additional quotes for comparison.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/analyze" className="btn-primary">
              Analyze Another Quote
            </Link>
            <button className="btn-secondary">Share Report</button>
          </div>
        </div>
      </div>
    </div>
  );
}
