import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

/**
 * SUNSET_MODE
 * When enabled, we serve the /sunset page for all routes.
 * This is used to rapidly de-publicize the legacy domain without deleting infrastructure.
 */
export function middleware(req: NextRequest) {
  const SUNSET_MODE = process.env.NEXT_PUBLIC_SUNSET_MODE === '1';
  if (!SUNSET_MODE) return NextResponse.next();

  const addSunsetHeaders = (res: NextResponse) => {
    res.headers.set('Cache-Control', 'no-store, no-cache, max-age=0, must-revalidate');
    res.headers.set('Pragma', 'no-cache');
    res.headers.set('Expires', '0');
    res.headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive, nosnippet');
    return res;
  };

  const { pathname } = req.nextUrl;

  // Allow Next internals + the sunset page itself
  if (
    pathname.startsWith('/_next') ||
    pathname === '/sunset' ||
    pathname === '/robots.txt' ||
    pathname === '/sitemap.xml' ||
    pathname === '/favicon.ico'
  ) {
    return addSunsetHeaders(NextResponse.next());
  }

  const url = req.nextUrl.clone();
  url.pathname = '/sunset';
  url.search = '';
  return addSunsetHeaders(NextResponse.rewrite(url));
}

export const config = {
  matcher: ['/((?!_next/static|_next/image).*)'],
};
