/**
 * Server-side API proxy helper for Next.js Route Handlers.
 *
 * Forwards requests to the backend and correctly relays Set-Cookie
 * headers back to the browser, solving the cross-domain cookie problem
 * that Next.js rewrites cannot handle.
 */
import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

export async function proxyRequest(
  req: NextRequest,
  backendPath: string,
  options?: { method?: string; body?: unknown }
): Promise<NextResponse> {
  const method = options?.method || req.method;
  const url = `${API_URL}${backendPath}`;

  // Forward cookies from browser to backend
  const cookieHeader = req.headers.get('cookie') || '';
  const contentType = req.headers.get('content-type') || '';

  const headers: Record<string, string> = {
    'Cookie': cookieHeader,
  };

  let body: BodyInit | undefined;

  if (options?.body !== undefined) {
    // Explicitly provided body — JSON encode it
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(options.body);
  } else if (['POST', 'PUT', 'PATCH'].includes(method)) {
    if (contentType.includes('multipart/form-data')) {
      // File upload — forward the raw body and let fetch set the boundary
      // Do NOT set Content-Type; fetch will set it with the correct boundary
      body = await req.arrayBuffer();
      headers['Content-Type'] = contentType;
    } else {
      // JSON body
      headers['Content-Type'] = 'application/json';
      try {
        const jsonBody = await req.json();
        body = JSON.stringify(jsonBody);
      } catch {
        // No body or invalid JSON — that's fine
      }
    }
  } else {
    // GET, DELETE, etc. — no body, set JSON content type for consistency
    headers['Content-Type'] = 'application/json';
  }

  const backendRes = await fetch(url, { method, headers, body });

  // Read backend response
  const data = await backendRes.text();

  // Build our response
  const res = new NextResponse(data, {
    status: backendRes.status,
    headers: {
      'Content-Type': backendRes.headers.get('Content-Type') || 'application/json',
    },
  });

  // Forward ALL Set-Cookie headers from backend to browser
  const setCookies = backendRes.headers.getSetCookie?.() || [];
  for (const cookie of setCookies) {
    res.headers.append('Set-Cookie', cookie);
  }

  // Fallback for environments where getSetCookie isn't available
  if (setCookies.length === 0) {
    const rawSetCookie = backendRes.headers.get('set-cookie');
    if (rawSetCookie) {
      const cookies = rawSetCookie.split(/,(?=\s*[a-zA-Z_][a-zA-Z0-9_]*=)/);
      for (const c of cookies) {
        res.headers.append('Set-Cookie', c.trim());
      }
    }
  }

  return res;
}
