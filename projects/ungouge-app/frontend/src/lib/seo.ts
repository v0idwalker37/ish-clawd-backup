/**
 * SEO Metadata for Ungouge.ai
 * Comprehensive metadata configuration for all pages including:
 * - OpenGraph tags
 * - Twitter cards
 * - JSON-LD structured data
 */

export interface PageMetadata {
  title: string;
  description: string;
  canonical?: string;
  ogImage?: string;
  noindex?: boolean;
}

// Base configuration
export const SITE_CONFIG = {
  name: 'Ungouge.ai',
  url: 'https://ungouge.ai',
  ogImage: 'https://ungouge.ai/opengraph-image', // Next.js dynamic OG image
  twitterHandle: '@ungougeai',
  brandColors: {
    primary: '#2563eb', // Blue
    secondary: '#10b981', // Green
  },
} as const;

// Default metadata (used as fallback)
export const DEFAULT_METADATA: PageMetadata = {
  title: 'Ungouge.ai – Fair Contractor Quote Analysis',
  description:
    'Stop getting gouged. Analyze contractor quotes against real BLS labor data. No lead gen, no contractor kickbacks – just honest pricing analysis.',
  canonical: SITE_CONFIG.url,
  ogImage: SITE_CONFIG.ogImage,
};

// Page-specific metadata
export const PAGE_METADATA: Record<string, PageMetadata> = {
  home: {
    title: 'Ungouge.ai – Fair Contractor Quote Analysis',
    description:
      'Is your contractor quote fair? Analyze quotes against real Bureau of Labor Statistics data. No lead gen, no contractor referrals – we work for you, not them.',
    canonical: `${SITE_CONFIG.url}/`,
    ogImage: `${SITE_CONFIG.url}/og-home.png`,
  },

  about: {
    title: 'About Ungouge.ai – Our Mission',
    description:
      'Learn why we built Ungouge.ai: to protect homeowners from contractor overcharges. We never sell your data or refer contractors. Ever.',
    canonical: `${SITE_CONFIG.url}/about`,
  },

  how_it_works: {
    title: 'How Ungouge.ai Works – Quote Analysis Process',
    description:
      'See how we analyze contractor quotes: BLS wage data, regional material costs, line-by-line breakdown. Our methodology explained in plain English.',
    canonical: `${SITE_CONFIG.url}/how-it-works`,
  },

  pricing: {
    title: 'Pricing – Ungouge.ai',
    description:
      '$19.99 per quote analysis. No subscriptions, no hidden fees, no lead gen. One price, full report, 100% money-back guarantee.',
    canonical: `${SITE_CONFIG.url}/pricing`,
  },

  search: {
    title: 'Search – Ungouge.ai',
    description:
      'Search your quote history and analysis reports.',
    canonical: `${SITE_CONFIG.url}/search`,
    noindex: true, // Search pages often have dynamic content
  },

  dashboard: {
    title: 'Dashboard – Ungouge.ai',
    description:
      'Your quote analysis dashboard. View reports, track savings, and manage your contractor quotes.',
    canonical: `${SITE_CONFIG.url}/dashboard`,
    noindex: true, // Private user content
  },

  new_report: {
    title: 'Analyze Quote – Ungouge.ai',
    description:
      'Upload your contractor quote for analysis. Get a detailed breakdown of fair pricing based on real labor and material data.',
    canonical: `${SITE_CONFIG.url}/analyze`,
    noindex: true, // Tool page
  },

  saved_reports: {
    title: 'My Reports – Ungouge.ai',
    description:
      'View all your quote analysis reports. Access your pricing breakdowns and negotiation tips anytime.',
    canonical: `${SITE_CONFIG.url}/reports`,
    noindex: true, // Private user content
  },

  settings: {
    title: 'Settings – Ungouge.ai',
    description: 'Manage your account settings, notification preferences, and privacy options.',
    canonical: `${SITE_CONFIG.url}/settings`,
    noindex: true, // Private user content
  },

  login: {
    title: 'Log In – Ungouge.ai',
    description: 'Log in to access your research reports and saved products.',
    canonical: `${SITE_CONFIG.url}/login`,
    noindex: true, // Don't index auth pages
  },

  signup: {
    title: 'Sign Up – Ungouge.ai',
    description:
      'Create your free Ungouge.ai account. Start researching products the honest way – no credit card required.',
    canonical: `${SITE_CONFIG.url}/signup`,
    noindex: true, // Don't index auth pages
  },

  blog: {
    title: 'Blog – Ungouge.ai',
    description:
      'Product research insights, buying guides, and industry analysis. Learn how to make smarter purchasing decisions.',
    canonical: `${SITE_CONFIG.url}/blog`,
  },
};

/**
 * Generate OpenGraph meta tags
 */
export function generateOpenGraphTags(metadata: PageMetadata) {
  return {
    'og:site_name': SITE_CONFIG.name,
    'og:title': metadata.title,
    'og:description': metadata.description,
    'og:url': metadata.canonical || SITE_CONFIG.url,
    'og:image': metadata.ogImage || SITE_CONFIG.ogImage,
    'og:type': 'website',
    'og:locale': 'en_US',
  };
}

/**
 * Generate Twitter Card meta tags
 */
export function generateTwitterCardTags(metadata: PageMetadata) {
  return {
    'twitter:card': 'summary_large_image',
    'twitter:site': SITE_CONFIG.twitterHandle,
    'twitter:title': metadata.title,
    'twitter:description': metadata.description,
    'twitter:image': metadata.ogImage || SITE_CONFIG.ogImage,
  };
}

/**
 * Generate JSON-LD structured data for Organization
 */
export function generateOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE_CONFIG.name,
    url: SITE_CONFIG.url,
    logo: `${SITE_CONFIG.url}/logo.png`,
    sameAs: [
      'https://twitter.com/ungouge',
      // Add more social profiles as needed
    ],
    description:
      'Contractor quote analysis powered by real BLS data. No lead gen, no contractor kickbacks – we protect homeowners from overcharges.',
    foundingDate: '2025',
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Support',
      email: 'support@ungouge.ai',
      availableLanguage: ['English'],
    },
  };
}

/**
 * Generate JSON-LD structured data for SoftwareApplication
 */
export function generateSoftwareApplicationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: SITE_CONFIG.name,
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '19.99',
      priceCurrency: 'USD',
      description: '$19.99 per quote analysis, 100% money-back guarantee',
    },
    description:
      'Analyze contractor quotes against Bureau of Labor Statistics data. Find out if you are being overcharged before you sign.',
    url: SITE_CONFIG.url,
    screenshot: `${SITE_CONFIG.url}/screenshot.png`,
    author: {
      '@type': 'Organization',
      name: SITE_CONFIG.name,
    },
  };
}

/**
 * Generate breadcrumb JSON-LD for page hierarchy
 */
export function generateBreadcrumbSchema(breadcrumbs: Array<{ name: string; url: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: crumb.url,
    })),
  };
}

/**
 * Get complete metadata for a specific page
 */
export function getPageMetadata(pageKey: string): PageMetadata {
  return PAGE_METADATA[pageKey] || DEFAULT_METADATA;
}

/**
 * Generate all meta tags for a page (for use in <head>)
 */
export function generateAllMetaTags(pageKey: string) {
  const metadata = getPageMetadata(pageKey);
  const ogTags = generateOpenGraphTags(metadata);
  const twitterTags = generateTwitterCardTags(metadata);

  return {
    title: metadata.title,
    description: metadata.description,
    canonical: metadata.canonical,
    ...(metadata.noindex && { robots: 'noindex, nofollow' }),
    ...ogTags,
    ...twitterTags,
  };
}

/**
 * Generate all structured data scripts for a page
 */
export function generateStructuredData(pageKey: string) {
  const schemas = [generateOrganizationSchema(), generateSoftwareApplicationSchema()];

  // Add page-specific schemas
  if (pageKey === 'home') {
    // Homepage gets all the structured data
    return schemas;
  }

  // For other pages, just include organization
  return [generateOrganizationSchema()];
}

/**
 * Helper to render JSON-LD scripts in React/Next.js
 */
export function renderJsonLd(schema: object) {
  return {
    // Escape '<' to prevent script injection via </script> breakout in JSON-LD
    __html: JSON.stringify(schema).replace(/</g, '\\u003c'),
  };
}
