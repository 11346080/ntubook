'use client';

/**
 * Client-side helper — use this in page.tsx / component (.tsx 'use client') code.
 *
 * Pattern: browser → Next.js rewrite → Django backend
 * All browser-facing Django calls go through /backend-api/ prefix.
 * next.config.ts rewrites /backend-api/:path* → ${DJANGO_API_ORIGIN}/api/:path*
 *
 * Environment:
 *   LOCAL:   DJANGO_API_ORIGIN not needed on client (rewrite is server-side)
 *   DEPLOY:  DJANGO_API_ORIGIN set on VM; client just uses /backend-api/
 */

const BACKEND_API_PREFIX = '/backend-api';

/**
 * Build a browser-safe Django API path.
 * Always starts with /backend-api/ (no leading slash needed in path arg).
 *
 * @example buildBackendApiPath('/core/program-types/') → '/backend-api/core/program-types/'
 * @example buildBackendApiPath('core/program-types/')  → '/backend-api/core/program-types/'
 * @example buildBackendApiPath('/accounts/me/')        → '/backend-api/accounts/me/'
 */
export function buildBackendApiPath(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  const stripped = normalized.replace(/^\/+/, ''); // strip any leading slashes
  return `${BACKEND_API_PREFIX}/${stripped}`;
}

/**
 * Build a full URL for Django media files.
 *
 * @example buildMediaUrl('/media/listings/cover.jpg') → '/backend-api/media/listings/cover.jpg'
 */
export function buildMediaUrl(filePath: string): string {
  const normalized = filePath.startsWith('/') ? filePath : `/${filePath}`;
  return buildBackendApiPath(normalized);
}
