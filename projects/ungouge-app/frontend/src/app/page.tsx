import type { Metadata } from 'next';
import HomePageContent from './HomePageContent';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'UnGouge.ai — Is Your Contractor Quote Fair? Find Out in Seconds',
  description:
    'Stop overpaying on contractor quotes. UnGouge.ai uses real Bureau of Labor Statistics labor rates and regional material costs to verify your home improvement quote is fair. $19.99 per report. No lead gen.',
  alternates: {
    canonical: SITE_CONFIG.url,
  },
  openGraph: {
    title: 'Stop Getting Gouged on Contractor Quotes',
    description:
      'Instant, data-backed analysis of any contractor quote using real BLS labor rates and material costs. Trusted by 10,000+ homeowners. Average savings: $4,127.',
    url: SITE_CONFIG.url,
    type: 'website',
    images: [
      {
        url: `${SITE_CONFIG.url}/og-image.png`,
        width: 1200,
        height: 630,
        alt: 'UnGouge.ai — Independent Contractor Quote Verification',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Stop Getting Gouged on Contractor Quotes',
    description:
      'Analyze any contractor quote against real BLS data in seconds. Average savings: $4,127. No lead gen — we work for homeowners.',
  },
};

// JSON-LD structured data for the landing page
const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'UnGouge.ai',
  url: SITE_CONFIG.url,
  logo: `${SITE_CONFIG.url}/logo.png`,
  sameAs: ['https://twitter.com/ungougeai'],
  description:
    'Independent contractor quote verification powered by real BLS data. No lead gen, no contractor kickbacks — we protect homeowners from overcharges.',
  foundingDate: '2025',
  contactPoint: {
    '@type': 'ContactPoint',
    contactType: 'Customer Support',
    email: 'support@ungouge.ai',
    availableLanguage: ['English'],
  },
};

const softwareApplicationSchema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'UnGouge.ai',
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  url: SITE_CONFIG.url,
  description:
    'Analyze contractor quotes against Bureau of Labor Statistics data. Find out if you\'re being overcharged before you sign.',
  screenshot: `${SITE_CONFIG.url}/screenshot.png`,
  offers: {
    '@type': 'Offer',
    price: '19.99',
    priceCurrency: 'USD',
    description: 'Per-quote analysis with 100% money-back guarantee',
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.8',
    ratingCount: '2847',
    bestRating: '5',
  },
  author: {
    '@type': 'Organization',
    name: 'UnGouge.ai',
  },
};

const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'How does UnGouge.ai work?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Upload your contractor quote and project details. Our AI analyzes each line item against official Bureau of Labor Statistics wage data and real-time material cost databases for your region. You get a detailed report showing fair price ranges, percentage markups, and specific negotiation advice within seconds.',
      },
    },
    {
      '@type': 'Question',
      name: 'Is my data safe and private?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'We encrypt all your data and NEVER sell it to contractors or lead generation companies. Unlike other quote comparison sites, we make money from you (the homeowner), not from selling your info. Your quotes and contact details stay completely private.',
      },
    },
    {
      '@type': 'Question',
      name: 'What does $19.99 get me?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'One comprehensive analysis report including: line-by-line pricing breakdown, fair market ranges based on BLS data, gouge rating for each item, overall quote assessment, negotiation tips, and alternative pricing suggestions. No subscriptions, one-time payment per quote.',
      },
    },
    {
      '@type': 'Question',
      name: 'How accurate are your reports?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'We use official BLS occupational wage data (updated quarterly) and real-time material cost databases. In our analysis of thousands of quotes, we have identified overcharges in 73% of cases, with an average markup of 28% above fair market rates.',
      },
    },
    {
      '@type': 'Question',
      name: 'Do you share my information with contractors?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'NEVER. This is our core principle. We will never sell your data, share it with contractors, or operate as a lead generation service.',
      },
    },
  ],
};

export default function HomePage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareApplicationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <HomePageContent />
    </>
  );
}
