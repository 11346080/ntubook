import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const djangoApiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

  // Read app_token from browser cookie
  const appToken = request.cookies.get('app_token')?.value;

  if (!appToken) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const response = await fetch(`${djangoApiBase}/api/accounts/me/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-App-Token': appToken,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data, { status: 200 });
  } catch {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 502 });
  }
}
