import type { Metadata } from 'next';
import Link from 'next/link';
import { getAllPosts } from '@/lib/blog';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'Blog — Home Improvement Cost Guides & Contractor Tips',
  description:
    'Expert guides on home improvement costs, contractor quote analysis, and renovation budgeting. Real pricing data to help you avoid overpaying.',
  alternates: {
    canonical: `${SITE_CONFIG.url}/blog`,
  },
  openGraph: {
    title: 'Blog — Home Improvement Cost Guides & Contractor Tips',
    description:
      'Expert guides on home improvement costs, contractor quote analysis, and renovation budgeting. Real pricing data to help you avoid overpaying.',
    url: `${SITE_CONFIG.url}/blog`,
    siteName: SITE_CONFIG.name,
    type: 'website',
  },
};

export default function BlogIndexPage() {
  const posts = getAllPosts();

  return (
    <div className="bg-white">
      {/* Hero */}
      <div className="bg-gradient-to-b from-primary-50 to-white">
        <div className="container mx-auto px-4 py-16 max-w-4xl text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Home Improvement Cost Guides
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Real pricing data, contractor tips, and cost breakdowns to help you
            make informed decisions — and avoid getting gouged.
          </p>
        </div>
      </div>

      {/* Posts Grid */}
      <div className="container mx-auto px-4 pb-20 max-w-4xl">
        <div className="space-y-8">
          {posts.map((post) => (
            <article
              key={post.slug}
              className="border-b border-gray-100 pb-8 last:border-b-0"
            >
              <Link
                href={`/blog/${post.slug}`}
                className="group block"
              >
                <div className="flex items-center gap-3 text-sm text-gray-500 mb-2">
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
                <h2 className="text-xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-2">
                  {post.title}
                </h2>
                <p className="text-gray-600 line-clamp-2">
                  {post.excerpt}
                </p>
              </Link>
            </article>
          ))}
        </div>

        {posts.length === 0 && (
          <p className="text-center text-gray-500 py-20">
            No posts yet. Check back soon!
          </p>
        )}
      </div>
    </div>
  );
}
