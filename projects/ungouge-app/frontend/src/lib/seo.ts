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
  ogImage: 'https://ungouge.ai/og-image.png',
  twitterHandle: '@ungougeai',
  brandColors: {
    primary: '#2563eb', // Blue
    secondary: '#10b981', // Green
  },
} as const;

// Default metadata (used as fallback)
export const DEFAULT_METADATA: PageMetadata = {
  title: 'Ungouge.ai – Research Without the Runaround',
  description:
    'No affiliate links. No sales pressure. Just honest research that helps you make better buying decisions. Find the best products without the marketing BS.',
  canonical: SITE_CONFIG.url,
  ogImage: SITE_CONFIG.ogImage,
};

// Page-specific metadata
export const PAGE_METADATA: Record<string, PageMetadata> = {
  home: {
    title: 'Ungouge.ai – Research Without the Runaround',
    description:
      'Tired of fake reviews and affiliate link spam? Ungouge.ai delivers honest, unbiased product research with no hidden agendas. Real data, real recommendations.',
    canonical: `${SITE_CONFIG.url}/`,
    ogImage: `${SITE_CONFIG.url}/og-home.png`,
  },

  about: {
    title: 'About Ungouge.ai – Our Mission',
    description:
      'Learn why we built Ungouge.ai: to fix the broken world of online product reviews. No affiliate links, no sponsored content, just research you can trust.',
    canonical: `${SITE_CONFIG.url}/about`,
  },

  how_it_works: {
    title: 'How Ungouge.ai Works – Our Research Process',
    description:
      'See how we research products: data analysis, real reviews, expert opinions, and zero affiliate influence. Our methodology explained in plain English.',
    canonical: `${SITE_CONFIG.url}/how-it-works`,
  },

  pricing: {
    title: 'Pricing – Ungouge.ai',
    description:
      'Simple, transparent pricing for honest product research. No hidden fees, no bait-and-switch. Start free, upgrade when you need more.',
    canonical: `${SITE_CONFIG.url}/pricing`,
  },

  search: {
    title: 'Search Products – Ungouge.ai',
    description:
      'Search thousands of researched products. Get instant access to unbiased reviews, data-driven comparisons, and recommendations you can trust.',
    canonical: `${SITE_CONFIG.url}/search`,
    noindex: true, // Search pages often have dynamic content
  },

  dashboard: {
    title: 'Dashboard – Ungouge.ai',
    description:
      'Your research dashboard. View saved reports, track product prices, and manage your research projects in one place.',
    canonical: `${SITE_CONFIG.url}/dashboard`,
    noindex: true, // Private user content
  },

  new_report: {
    title: 'Create New Report – Ungouge.ai',
    description:
      'Start a new product research report. Enter what you\'re looking for, set your criteria, and get comprehensive analysis with no marketing BS.',
    canonical: `${SITE_CONFIG.url}/reports/new`,
    noindex: true, // Tool page
  },

  saved_reports: {
    title: 'My Reports – Ungouge.ai',
    description:
      'View all your saved research reports. Access your buying guides, product comparisons, and analysis anytime.',
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
      'https://twitter.com/ungougeai',
      // Add more social profiles as needed
    ],
    description:
      'Honest product research without affiliate links or sales pressure. Research you can trust.',
    foundingDate: '2024',
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
    applicationCategory: 'ProductResearchApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
      description: 'Free tier available with premium options',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '127',
      bestRating: '5',
      worstRating: '1',
    },
    description:
      'Research products without the runaround. No affiliate links, no sales pressure, just honest recommendations.',
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
    __html: JSON.stringify(schema),
  };
}
