import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ChatWidget from '@/components/ChatWidget';
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
    template: '%s | Ungouge.ai',
  },
  description: DEFAULT_METADATA.description,
  keywords: [
    'contractor quote analysis',
    'fair contractor pricing',
    'quote verification',
    'contractor overcharge',
    'home improvement quotes',
    'BLS labor data',
    'no lead gen',
    'homeowner protection',
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
    description: DEFAULT_METADATA.description,
    images: [
      {
        url: DEFAULT_METADATA.ogImage!,
        width: 1200,
        height: 630,
        alt: 'Ungouge.ai - Research Without the Runaround',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: SITE_CONFIG.twitterHandle,
    creator: SITE_CONFIG.twitterHandle,
    title: DEFAULT_METADATA.title,
    description: DEFAULT_METADATA.description,
    images: [DEFAULT_METADATA.ogImage!],
  },
  alternates: {
    canonical: DEFAULT_METADATA.canonical,
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
          <ChatWidget />
        </div>
      </body>
    </html>
  );
}
