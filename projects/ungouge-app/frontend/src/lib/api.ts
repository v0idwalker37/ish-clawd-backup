/**
 * Centralized API client with automatic auth handling
 * 
 * Features:
 * - Automatic credentials (cookies) on all requests
 * - 401 handling with redirect to login
 * - Consistent error parsing
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiError {
  error: string;
  suggestion?: string;
  detail?: string | { error: string; suggestion?: string };
}

/**
 * Parse API error response into user-friendly message
 */
export function parseApiError(error: any): string {
  // If it's already a string, return it
  if (typeof error === 'string') return error;
  
  // Check for our custom exception format
  if (error?.error) {
    return error.suggestion 
      ? `${error.error}. ${error.suggestion}`
      : error.error;
  }
  
  // Check for FastAPI detail format
  if (error?.detail) {
    if (typeof error.detail === 'string') return error.detail;
    if (error.detail.error) {
      return error.detail.suggestion
        ? `${error.detail.error}. ${error.detail.suggestion}`
        : error.detail.error;
    }
  }
  
  // Fallback
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Make an authenticated API request
 */
export async function apiFetch<T = any>(
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
  get: <T = any>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'GET' }),
  
  post: <T = any>(endpoint: string, body?: any, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  put: <T = any>(endpoint: string, body?: any, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  delete: <T = any>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'DELETE' }),
};

export default api;
