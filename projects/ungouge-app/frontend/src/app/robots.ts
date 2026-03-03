import type { MetadataRoute } from 'next';

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://gougealert.com';
const SUNSET_MODE = process.env.NEXT_PUBLIC_SUNSET_MODE === '1';

export default function robots(): MetadataRoute.Robots {
  if (SUNSET_MODE) {
    return {
      rules: [
        {
          userAgent: '*',
          disallow: '/',
        },
      ],
    };
  }

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/dashboard/', '/api/', '/report/', '/login', '/register'],
      },
    ],
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
