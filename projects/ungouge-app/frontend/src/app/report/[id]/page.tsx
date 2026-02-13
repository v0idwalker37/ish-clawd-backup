'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import axios from 'axios';
import ReportCard from '@/components/ReportCard';
import PriceGauge from '@/components/PriceGauge';
import { ArrowLeft, Download, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
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
  const searchParams = useSearchParams();
  const reportId = params.id as string;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfDownloading, setPdfDownloading] = useState(false);
  const [showPaymentSuccess, setShowPaymentSuccess] = useState(false);

  // Payment success banner
  useEffect(() => {
    if (searchParams.get('payment') === 'success') {
      setShowPaymentSuccess(true);
      const timer = setTimeout(() => setShowPaymentSuccess(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [searchParams]);

  // PDF download handler
  const handleDownloadPdf = useCallback(async () => {
    if (pdfDownloading) return;
    setPdfDownloading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/quotes/${reportId}/pdf`, {
        withCredentials: true,
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ungouge-report-${reportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download failed:', err);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setPdfDownloading(false);
    }
  }, [reportId, pdfDownloading]);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`, {
          withCredentials: true,  // Send auth cookies
        });
        setReport(response.data);
      } catch (err: unknown) {
        if (axios.isAxiosError(err)) {
          if (err.response?.status === 401) {
            setError('Please log in to view this report.');
          } else if (err.response?.status === 403) {
            setError('You do not have permission to view this report.');
          } else if (err.response?.status === 404) {
            setError('Report not found. Please check your report ID.');
          } else {
            setError('Failed to load report. Please try again later.');
          }
        } else {
          setError('Failed to load report. Please check your connection.');
        }
        console.error('Report fetch error:', err);
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

        {/* Payment Success Banner */}
        {showPaymentSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3 animate-in fade-in duration-300">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            <p className="text-green-800 font-medium">Payment confirmed! Your report is ready.</p>
          </div>
        )}

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
            <button
              onClick={handleDownloadPdf}
              disabled={pdfDownloading}
              className="btn-secondary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {pdfDownloading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              {pdfDownloading ? 'Generating...' : 'Download PDF'}
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
