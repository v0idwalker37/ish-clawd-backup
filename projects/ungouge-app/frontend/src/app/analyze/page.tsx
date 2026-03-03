import type { Metadata } from 'next';
import AnalyzePageContent from './AnalyzePageContent';

export const metadata: Metadata = {
  title: 'Analyze Your Contractor Quote',
  description:
    'Upload your contractor quote for instant, data-backed analysis. Compare line-item pricing against real BLS labor rates and regional material costs. Get your report in seconds.',
  alternates: {
    canonical: 'https://gougealert.com/analyze',
  },
  openGraph: {
    title: 'Analyze Your Contractor Quote — GougeAlert',
    description:
      'Upload your quote and get instant analysis against real BLS labor data. Know if you\'re being overcharged before you sign.',
    url: 'https://gougealert.com/analyze',
  },
};

export default function AnalyzePage() {
  return <AnalyzePageContent />;
}
