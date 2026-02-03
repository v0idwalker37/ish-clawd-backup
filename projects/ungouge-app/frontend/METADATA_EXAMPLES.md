# SEO Metadata Usage Examples

Quick reference for adding metadata to Next.js 14 app router pages.

## Basic Page Metadata

```typescript
// app/about/page.tsx
import { Metadata } from 'next';
import { generateAllMetaTags } from '@/lib/seo';

export const metadata: Metadata = generateAllMetaTags('about');

export default function AboutPage() {
  return <div>About page content</div>;
}
```

## Available Page Keys

Use these keys with `generateAllMetaTags(key)`:

- `'home'` - Homepage
- `'about'` - About page
- `'how_it_works'` - How it works
- `'pricing'` - Pricing page
- `'search'` - Search page
- `'dashboard'` - User dashboard
- `'new_report'` - Create report page
- `'saved_reports'` - My reports page
- `'settings'` - Settings page
- `'login'` - Login page
- `'signup'` - Signup page
- `'blog'` - Blog index

## Custom Page Metadata

```typescript
// app/custom/page.tsx
import { Metadata } from 'next';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'Custom Page Title',
  description: 'Custom page description',
  alternates: {
    canonical: `${SITE_CONFIG.url}/custom`,
  },
  openGraph: {
    title: 'Custom Page Title',
    description: 'Custom page description',
    url: `${SITE_CONFIG.url}/custom`,
    images: [
      {
        url: `${SITE_CONFIG.url}/custom-og-image.png`,
        width: 1200,
        height: 630,
      },
    ],
  },
};

export default function CustomPage() {
  return <div>Custom content</div>;
}
```

## Dynamic Pages

```typescript
// app/reports/[id]/page.tsx
import { Metadata } from 'next';
import { SITE_CONFIG } from '@/lib/seo';

type Props = {
  params: { id: string };
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  // Fetch report data
  const report = await getReport(params.id);

  return {
    title: report.title,
    description: report.summary,
    alternates: {
      canonical: `${SITE_CONFIG.url}/reports/${params.id}`,
    },
    openGraph: {
      title: report.title,
      description: report.summary,
      url: `${SITE_CONFIG.url}/reports/${params.id}`,
      type: 'article',
      publishedTime: report.createdAt,
    },
  };
}

export default function ReportPage({ params }: Props) {
  return <div>Report {params.id}</div>;
}
```

## Adding Breadcrumbs (JSON-LD)

```typescript
// app/blog/[slug]/page.tsx
import { generateBreadcrumbSchema, renderJsonLd, SITE_CONFIG } from '@/lib/seo';

export default function BlogPost({ params }: { params: { slug: string } }) {
  const breadcrumbs = [
    { name: 'Home', url: SITE_CONFIG.url },
    { name: 'Blog', url: `${SITE_CONFIG.url}/blog` },
    { name: 'Article Title', url: `${SITE_CONFIG.url}/blog/${params.slug}` },
  ];

  const breadcrumbSchema = generateBreadcrumbSchema(breadcrumbs);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={renderJsonLd(breadcrumbSchema)}
      />
      <article>{/* Blog content */}</article>
    </>
  );
}
```

## No-Index Pages (Private Content)

```typescript
// app/dashboard/settings/page.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Account Settings',
  description: 'Manage your Ungouge.ai account settings',
  robots: {
    index: false,
    follow: false,
  },
};

export default function SettingsPage() {
  return <div>Private settings</div>;
}
```

## Testing Metadata

1. **View in browser:**
   - Right-click → Inspect → Elements tab → `<head>`

2. **Meta tag testing tools:**
   - https://metatags.io
   - https://cards-dev.twitter.com/validator
   - https://www.linkedin.com/post-inspector/

3. **Structured data testing:**
   - https://search.google.com/test/rich-results
   - https://validator.schema.org

4. **Local test:**
   ```bash
   npm run build
   npm run start
   # Then view page source
   ```

## Common Patterns

### Blog Post with Author

```typescript
export const metadata: Metadata = {
  title: 'How to Choose a Dishwasher',
  description: 'Complete buying guide...',
  authors: [{ name: 'Ungouge Research Team' }],
  openGraph: {
    type: 'article',
    publishedTime: '2024-01-15T00:00:00.000Z',
    modifiedTime: '2024-01-20T00:00:00.000Z',
    authors: ['Ungouge Research Team'],
  },
};
```

### Product Page

```typescript
export const metadata: Metadata = {
  title: 'Best Dishwashers Under $600',
  description: 'We analyzed 47 dishwashers...',
  openGraph: {
    type: 'article',
  },
};

// Add Product schema in component:
const productSchema = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: 'Best Dishwashers Under $600',
  description: 'Comprehensive research...',
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.5',
    reviewCount: '23',
  },
};

return (
  <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(productSchema) }}
    />
    <div>{/* Product content */}</div>
  </>
);
```

## Quick Checklist

For every public page, ensure:
- ✓ Unique title (< 60 characters)
- ✓ Unique description (150-160 characters)
- ✓ Canonical URL set
- ✓ OpenGraph image (1200×630)
- ✓ Relevant keywords in description
- ✓ No duplicate content across pages

For private/tool pages:
- ✓ Add `robots: { index: false }`
- ✓ Still provide title/description (for bookmarks)
