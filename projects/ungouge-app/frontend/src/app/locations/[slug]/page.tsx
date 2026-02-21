import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getAllLocationSlugs, getLocationBySlug } from '@/lib/locations';
import { SITE_CONFIG, renderJsonLd } from '@/lib/seo';

interface LocationPageProps {
  params: { slug: string };
}

export async function generateStaticParams() {
  const slugs = getAllLocationSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: LocationPageProps): Promise<Metadata> {
  const location = await getLocationBySlug(params.slug);
  if (!location) return {};

  return {
    title: location.title,
    description: location.description,
    keywords: location.keywords,
    authors: [{ name: location.author }],
    alternates: {
      canonical: `${SITE_CONFIG.url}/locations/${location.slug}`,
    },
    openGraph: {
      title: location.title,
      description: location.description,
      url: `${SITE_CONFIG.url}/locations/${location.slug}`,
      siteName: SITE_CONFIG.name,
      type: 'website',
    },
  };
}

export default async function LocationPage({ params }: LocationPageProps) {
  const location = await getLocationBySlug(params.slug);

  if (!location) {
    notFound();
  }

  // LocalBusiness structured data
  const localBusinessSchema = {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    name: `${SITE_CONFIG.name} - ${location.title.split(' ')[0]}`,
    description: location.description,
    areaServed: {
      '@type': 'State',
      name: location.title.split(' ')[0],
    },
    url: `${SITE_CONFIG.url}/locations/${location.slug}`,
  };

  // Breadcrumb structured data
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: SITE_CONFIG.url,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Locations',
        item: `${SITE_CONFIG.url}/locations`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: location.title.split(' ')[0],
        item: `${SITE_CONFIG.url}/locations/${location.slug}`,
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={renderJsonLd(localBusinessSchema)}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={renderJsonLd(breadcrumbSchema)}
      />

      <div className="bg-white">
        <article className="container mx-auto px-4 py-12 max-w-3xl">
          {/* Back link */}
          <Link
            href="/locations"
            className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium mb-8 group"
          >
            <svg
              className="w-4 h-4 mr-1 transition-transform group-hover:-translate-x-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            All Locations
          </Link>

          {/* Header */}
          <header className="mb-10">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 leading-tight mb-4">
              {location.title}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
              <span>📍 {location.majorCities.join(', ')}</span>
            </div>
          </header>

          {/* Content */}
          <div
            className="blog-prose"
            dangerouslySetInnerHTML={{ __html: location.contentHtml }}
          />
        </article>
      </div>
    </>
  );
}
