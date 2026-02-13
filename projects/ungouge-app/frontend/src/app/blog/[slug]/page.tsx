import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getAllPostSlugs, getPostBySlug } from '@/lib/blog';
import { SITE_CONFIG, renderJsonLd } from '@/lib/seo';

interface BlogPostPageProps {
  params: { slug: string };
}

export async function generateStaticParams() {
  const slugs = getAllPostSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: BlogPostPageProps): Promise<Metadata> {
  const post = await getPostBySlug(params.slug);
  if (!post) return {};

  return {
    title: post.title,
    description: post.description,
    keywords: post.keywords,
    authors: [{ name: post.author }],
    alternates: {
      canonical: `${SITE_CONFIG.url}/blog/${post.slug}`,
    },
    openGraph: {
      title: post.title,
      description: post.description,
      url: `${SITE_CONFIG.url}/blog/${post.slug}`,
      siteName: SITE_CONFIG.name,
      type: 'article',
      publishedTime: post.date,
      authors: [post.author],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.description,
      site: SITE_CONFIG.twitterHandle,
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const post = await getPostBySlug(params.slug);

  if (!post) {
    notFound();
  }

  // Article structured data
  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    dateModified: post.date,
    author: {
      '@type': 'Organization',
      name: post.author,
      url: SITE_CONFIG.url,
    },
    publisher: {
      '@type': 'Organization',
      name: SITE_CONFIG.name,
      url: SITE_CONFIG.url,
      logo: {
        '@type': 'ImageObject',
        url: `${SITE_CONFIG.url}/logo.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${SITE_CONFIG.url}/blog/${post.slug}`,
    },
    keywords: post.keywords.join(', '),
    wordCount: post.content.split(/\s+/).length,
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
        name: 'Blog',
        item: `${SITE_CONFIG.url}/blog`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: post.title,
        item: `${SITE_CONFIG.url}/blog/${post.slug}`,
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={renderJsonLd(articleSchema)}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={renderJsonLd(breadcrumbSchema)}
      />

      <div className="bg-white">
        <article className="container mx-auto px-4 py-12 max-w-3xl">
          {/* Back link */}
          <Link
            href="/blog"
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
            Back to Blog
          </Link>

          {/* Header */}
          <header className="mb-10">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 leading-tight mb-4">
              {post.title}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
              <span>{post.author}</span>
              <span>·</span>
              <time dateTime={post.date}>
                {new Date(post.date + 'T00:00:00').toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </time>
              <span>·</span>
              <span>{post.readingTime} min read</span>
            </div>
          </header>

          {/* Content */}
          <div
            className="blog-prose"
            dangerouslySetInnerHTML={{ __html: post.contentHtml }}
          />

          {/* Footer CTA */}
          <div className="mt-16 p-8 bg-primary-50 rounded-2xl text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Got a contractor quote?
            </h3>
            <p className="text-gray-600 mb-6">
              Upload it and get an independent analysis backed by real labor and
              material cost data. No lead gen — we work for you.
            </p>
            <Link
              href="/analyze"
              className="inline-block bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Analyze Your Quote
            </Link>
          </div>
        </article>
      </div>
    </>
  );
}
