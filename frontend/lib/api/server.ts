/**
 * Server-side helper — use this ONLY in route.ts, server components, or server-side helpers.
 *
 * DJANGO_API_ORIGIN is the server-only base origin (no /api suffix).
 * Examples:
 *   LOCAL:  http://localhost:8000
 *   DEPLOY: http://127.0.0.1:8000
 *
 * Never expose DJANGO_API_ORIGIN to client-side code.
 */

const DJANGO_API_ORIGIN = process.env.DJANGO_API_ORIGIN ?? 'http://localhost:8000';

/**
 * Build a full Django backend URL for server-side (route.ts / server component) use.
 * Handles trailing/leading slashes automatically. Never doubles /api.
 *
 * @example buildDjangoApiUrl('/accounts/me/')   → 'http://localhost:8000/api/accounts/me/'
 * @example buildDjangoApiUrl('accounts/me/')   → 'http://localhost:8000/api/accounts/me/'
 * @example buildDjangoApiUrl('/accounts/me')   → 'http://localhost:8000/api/accounts/me'
 * @example buildDjangoApiUrl('core/program-types/') → 'http://localhost:8000/api/core/program-types/'
 */
export function buildDjangoApiUrl(path: string): string {
  // Strip leading/trailing slashes from path
  const stripped = path.replace(/^\/+|\/+$/g, '');
  return `${DJANGO_API_ORIGIN}/api/${stripped}`;
}

/**
 * Get the frontend base URL (used for redirects).
 * Falls back to http://localhost:3000 for local dev.
 */
export function getFrontendBase(): string {
  return process.env.NEXTAUTH_URL ?? 'http://localhost:3000';
}
