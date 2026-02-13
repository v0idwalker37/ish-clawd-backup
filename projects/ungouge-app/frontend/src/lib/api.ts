/**
 * Centralized API client with automatic auth handling
 * 
 * Features:
 * - Automatic credentials (cookies) on all requests
 * - 401 handling with redirect to login
 * - Consistent error parsing
 */

// Use relative URLs in the browser (proxied via Next.js rewrites in next.config.js).
// Server-side code should use process.env.API_URL (non-public, never leaked to client).
const API_URL = typeof window !== 'undefined' ? '' : (process.env.API_URL || 'http://localhost:8000');

interface ApiError {
  error: string;
  suggestion?: string;
  detail?: string | { error: string; suggestion?: string };
}

/**
 * Parse API error response into user-friendly message
 */
export function parseApiError(error: unknown): string {
  // If it's already a string, return it
  if (typeof error === 'string') return error;

  if (typeof error !== 'object' || error === null) {
    return 'An unexpected error occurred. Please try again.';
  }
  
  const err = error as Record<string, unknown>;
  
  // Check for our custom exception format
  if (typeof err.error === 'string') {
    return typeof err.suggestion === 'string'
      ? `${err.error}. ${err.suggestion}`
      : err.error;
  }
  
  // Check for FastAPI detail format
  if (err.detail != null) {
    if (typeof err.detail === 'string') return err.detail;
    if (typeof err.detail === 'object') {
      const detail = err.detail as Record<string, unknown>;
      if (typeof detail.error === 'string') {
        return typeof detail.suggestion === 'string'
          ? `${detail.error}. ${detail.suggestion}`
          : detail.error;
      }
    }
  }
  
  // Fallback
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Make an authenticated API request
 */
export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    credentials: 'include',  // Always send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  // Handle 401 - redirect to login
  if (response.status === 401) {
    // Only redirect in browser context
    if (typeof window !== 'undefined') {
      // Clear any stale data
      localStorage.clear();
      sessionStorage.clear();
      
      // Redirect to login with return URL
      const returnUrl = encodeURIComponent(window.location.pathname);
      window.location.href = `/login?session_expired=true&return=${returnUrl}`;
    }
    throw new Error('Session expired. Please log in again.');
  }
  
  // Parse response
  const data = await response.json().catch(() => ({}));
  
  // Handle other errors
  if (!response.ok) {
    throw new Error(parseApiError(data));
  }
  
  return data as T;
}

/**
 * Convenience methods
 */
export const api = {
  get: <T = unknown>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'GET' }),
  
  post: <T = unknown>(endpoint: string, body?: unknown, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  put: <T = unknown>(endpoint: string, body?: unknown, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  delete: <T = unknown>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'DELETE' }),
};

export default api;
