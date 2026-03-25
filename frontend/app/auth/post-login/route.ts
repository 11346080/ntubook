import { NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function GET() {
  const frontendBase = process.env.NEXTAUTH_URL ?? 'http://localhost:3000';
  // NOTE: NEXT_PUBLIC_API_URL must NOT include /api (e.g. https://test.ntubook.com)
  const djangoApiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

  // 1. Get authenticated session (NextAuth JWT)
  const session = await auth();

  if (!session?.user) {
    return NextResponse.redirect(new URL('/login', frontendBase));
  }

  const { sub, email, name } = session.user as { sub: string; email: string; name?: string };

  if (!sub || !email) {
    return NextResponse.redirect(new URL('/login?error=InvalidSession', frontendBase));
  }

  // 2. Server-to-server: call Django bootstrap endpoint
  const bootstrapSecret = process.env.AUTH_DJANGO_BOOTSTRAP_SECRET;

  if (!bootstrapSecret) {
    console.error('[post-login] AUTH_DJANGO_BOOTSTRAP_SECRET is not set');
    return NextResponse.redirect(new URL('/login?error=ServerConfigError', frontendBase));
  }

  let bootstrapResponse: Response;
  try {
    bootstrapResponse = await fetch(`${djangoApiBase}/api/accounts/bootstrap/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Bootstrap-Secret': bootstrapSecret,
      },
      body: JSON.stringify({
        google_sub: sub,
        email: email,
        name: name ?? '',
      }),
    });
  } catch (networkErr) {
    console.error('[post-login] Django bootstrap fetch failed:', networkErr);
    return NextResponse.redirect(new URL('/login?error=BackendUnreachable', frontendBase));
  }

  let result: {
    app_token?: string;
    is_new_user?: boolean;
    has_profile?: boolean;
    error?: string;
    reason?: string;
  };
  try {
    result = await bootstrapResponse.json();
  } catch {
    console.error('[post-login] Failed to parse Django bootstrap response');
    return NextResponse.redirect(new URL('/login?error=BackendError', frontendBase));
  }

  if (!bootstrapResponse.ok) {
    console.error('[post-login] Bootstrap failed:', result);
    // Propagate error reason for debugging
    const errParam = encodeURIComponent(result.reason ?? result.error ?? 'BootstrapFailed');
    return NextResponse.redirect(new URL(`/login?error=BootstrapFailed&reason=${errParam}`, frontendBase));
  }

  const { app_token, is_new_user, has_profile } = result;

  if (!app_token) {
    console.error('[post-login] No app_token in bootstrap response');
    return NextResponse.redirect(new URL('/login?error=BackendError', frontendBase));
  }

  // 3. Determine redirect destination
  let redirectUrl = '/dashboard';

  if (is_new_user || !has_profile) {
    redirectUrl = '/first-login';
  }

  // 4. Set HttpOnly + SameSite=Lax app_token cookie and redirect
  const isProduction = process.env.NODE_ENV === 'production';
  const cookieMaxAge = 30 * 24 * 60 * 60; // 30 days in seconds

  const response = NextResponse.redirect(new URL(redirectUrl, frontendBase));
  response.cookies.set('app_token', app_token, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    maxAge: cookieMaxAge,
    secure: isProduction,
  });

  return response;
}
