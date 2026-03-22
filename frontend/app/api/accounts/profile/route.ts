import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const DJANGO_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function authedFetch(request: NextRequest, method: string) {
  const appToken = request.cookies.get('app_token')?.value;
  if (!appToken) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-App-Token': appToken,
  };

  if (method === 'GET') {
    return fetch(`${DJANGO_BASE}/api/accounts/profile/`, { method, headers });
  }

  return request.json().then(body =>
    fetch(`${DJANGO_BASE}/api/accounts/profile/`, {
      method,
      headers,
      body: JSON.stringify(body),
    })
  ).catch(() =>
    NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  );
}

export async function GET(request: NextRequest) {
  const response = await authedFetch(request, 'GET');
  if (response instanceof Response) {
    const data = await response.json();
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }
    return NextResponse.json(data, { status: response.status });
  }
  return response;
}

export async function POST(request: NextRequest) {
  const response = await authedFetch(request, 'POST');
  if (response instanceof Response) {
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  }
  return response;
}

export async function PATCH(request: NextRequest) {
  const response = await authedFetch(request, 'PATCH');
  if (response instanceof Response) {
    const data = await response.json();
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }
    return NextResponse.json(data, { status: response.status });
  }
  return response;
}
