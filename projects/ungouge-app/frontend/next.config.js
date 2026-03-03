/** @type {import('next').NextConfig} */
const primaryApiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN || 'https://api.gougealert.com';
const legacyApiOrigin = process.env.NEXT_PUBLIC_LEGACY_API_ORIGIN || 'https://api.ungouge.ai';

const connectSrc = [
  "'self'",
  primaryApiOrigin,
  legacyApiOrigin,
  'https://gemini.googleapis.com',
  'https://api.stripe.com',
  'https://*.stripe.com',
  'https://plausible.io',
].join(' ');

const sunsetMode = process.env.NEXT_PUBLIC_SUNSET_MODE === '1';

const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com https://plausible.io; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src ${connectSrc}; frame-src https://js.stripe.com;`,
          },
          ...(sunsetMode
            ? [
                {
                  key: 'X-Robots-Tag',
                  value: 'noindex, nofollow, noarchive, nosnippet',
                },
              ]
            : []),
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  // API routes are handled by Next.js Route Handlers in src/app/api/
  // which properly forward Set-Cookie headers from the backend.
  // The old rewrite approach lost cookies across domains.
};

module.exports = nextConfig;
