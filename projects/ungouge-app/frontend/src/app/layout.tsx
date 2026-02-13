import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ChatWidget from '@/components/ChatWidget';
import CookieConsent from '@/components/CookieConsent';
import ErrorBoundary from '@/components/ErrorBoundary';
import {
  DEFAULT_METADATA,
  SITE_CONFIG,
  generateOpenGraphTags,
  generateTwitterCardTags,
  generateOrganizationSchema,
  generateSoftwareApplicationSchema,
  renderJsonLd,
} from '@/lib/seo';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

// Default metadata for all pages (can be overridden per page)
export const metadata: Metadata = {
  metadataBase: new URL(SITE_CONFIG.url),
  title: {
    default: DEFAULT_METADATA.title,
    template: '%s | UnGouge — Independent Quote Verification',
  },
  description:
    'Is your contractor quote fair? UnGouge.ai analyzes contractor quotes against real Bureau of Labor Statistics labor rates and regional material costs. Independent, data-backed price verification for homeowners — no lead gen, no contractor kickbacks.',
  keywords: [
    'contractor quote verification',
    'home improvement pricing',
    'contractor quote analysis',
    'fair contractor pricing',
    'is my contractor quote fair',
    'contractor overcharge',
    'home renovation cost check',
    'BLS labor data',
    'contractor price comparison',
    'home improvement quote analyzer',
    'independent quote verification',
    'homeowner protection',
    'no lead gen',
    'kitchen remodel cost',
    'bathroom renovation pricing',
    'roofing quote check',
  ],
  authors: [{ name: 'Ungouge.ai Team' }],
  creator: 'Ungouge.ai',
  publisher: 'Ungouge.ai',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: SITE_CONFIG.url,
    siteName: SITE_CONFIG.name,
    title: DEFAULT_METADATA.title,
    description:
      'Stop overpaying on contractor quotes. UnGouge.ai uses real BLS labor data and regional material costs to verify your quote is fair. Trusted by 10,000+ homeowners.',
    images: [
      {
        url: DEFAULT_METADATA.ogImage!,
        width: 1200,
        height: 630,
        alt: 'UnGouge.ai — Independent Contractor Quote Verification',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: SITE_CONFIG.twitterHandle,
    creator: SITE_CONFIG.twitterHandle,
    title: DEFAULT_METADATA.title,
    description:
      'Is your contractor quote fair? Analyze it against real BLS data in seconds. No lead gen — we work for homeowners, not contractors.',
    images: [DEFAULT_METADATA.ogImage!],
  },
  alternates: {
    canonical: DEFAULT_METADATA.canonical,
  },
  other: {
    'theme-color': '#2563eb',
  },
  verification: {
    // Add verification codes when available
    // google: 'your-google-verification-code',
    // yandex: 'your-yandex-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Generate structured data schemas
  const organizationSchema = generateOrganizationSchema();
  const softwareSchema = generateSoftwareApplicationSchema();

  return (
    <html lang="en">
      <head>
        {/* JSON-LD Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={renderJsonLd(organizationSchema)}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={renderJsonLd(softwareSchema)}
        />
      </head>
      <body className={inter.variable}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <ErrorBoundary>
            <main className="flex-grow">{children}</main>
          </ErrorBoundary>
          <Footer />
          <CookieConsent />
          <ChatWidget />
        </div>
      </body>
    </html>
  );
}
