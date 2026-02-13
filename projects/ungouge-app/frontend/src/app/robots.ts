import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/dashboard/', '/api/', '/report/', '/login', '/register'],
      },
    ],
    sitemap: 'https://ungouge.ai/sitemap.xml',
  };
}
