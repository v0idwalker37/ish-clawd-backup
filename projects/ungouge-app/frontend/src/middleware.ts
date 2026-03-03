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

  const { pathname } = req.nextUrl;

  // Allow Next internals + the sunset page itself
  if (
    pathname.startsWith('/_next') ||
    pathname === '/sunset' ||
    pathname === '/robots.txt' ||
    pathname === '/sitemap.xml' ||
    pathname === '/favicon.ico'
  ) {
    return NextResponse.next();
  }

  const url = req.nextUrl.clone();
  url.pathname = '/sunset';
  url.search = '';
  return NextResponse.rewrite(url);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image).*)'],
};
