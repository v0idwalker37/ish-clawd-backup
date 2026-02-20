/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: 'https://ungouge.ai',
  generateRobotsTxt: true,
  changefreq: 'weekly',
  priority: 0.7,
  sitemapSize: 5000,
  exclude: [
    '/dashboard*',
    '/login',
    '/register',
    '/verify-email*',
    '/reset-password*',
    '/api/*',
    '/report/*',   // individual reports are private
  ],
  robotsTxtOptions: {
    policies: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/dashboard', '/api/', '/report/'],
      },
    ],
    additionalSitemaps: [],
  },
  // Boost priority for key pages
  transform: async (config, path) => {
    // Homepage
    if (path === '/') {
      return { loc: path, changefreq: 'weekly', priority: 1.0, lastmod: new Date().toISOString() };
    }
    // Analyze page (main CTA)
    if (path === '/analyze') {
      return { loc: path, changefreq: 'weekly', priority: 0.9, lastmod: new Date().toISOString() };
    }
    // Blog index
    if (path === '/blog') {
      return { loc: path, changefreq: 'daily', priority: 0.8, lastmod: new Date().toISOString() };
    }
    // Individual blog posts
    if (path.startsWith('/blog/')) {
      return { loc: path, changefreq: 'monthly', priority: 0.7, lastmod: new Date().toISOString() };
    }
    // About, pricing
    if (['/about', '/pricing'].includes(path)) {
      return { loc: path, changefreq: 'monthly', priority: 0.8, lastmod: new Date().toISOString() };
    }
    // Legal pages
    if (['/privacy', '/terms'].includes(path)) {
      return { loc: path, changefreq: 'yearly', priority: 0.3, lastmod: new Date().toISOString() };
    }
    // Default
    return { loc: path, changefreq: config.changefreq, priority: config.priority, lastmod: new Date().toISOString() };
  },
};
