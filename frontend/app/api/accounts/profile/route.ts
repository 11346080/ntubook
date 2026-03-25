import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const DJANGO_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function djangoFetch(
  request: NextRequest,
  method: string,
  body?: unknown,
) {
  const appToken = request.cookies.get('app_token')?.value;
  if (!appToken) {
    return { status: 401, body: { error: 'Unauthorized' } };
  }

  const url = `${DJANGO_BASE}/api/accounts/profile/`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-App-Token': appToken,
  };

  const fetchOpts: RequestInit = { method, headers };
  if (body) fetchOpts.body = JSON.stringify(body);

  let djangoResponse: Response;
  try {
    djangoResponse = await fetch(url, fetchOpts);
  } catch (err) {
    return { status: 502, body: { error: 'Django unreachable', detail: String(err) } };
  }

  // Read raw text first so we can handle both JSON and non-JSON responses
  const rawText = await djangoResponse.text();

  let data: unknown;
  try {
    data = JSON.parse(rawText);
  } catch {
    return {
      status: djangoResponse.status,
      body: { error: 'Django returned non-JSON', raw: rawText.slice(0, 200) },
    };
  }

  return { status: djangoResponse.status, body: data };
}

export async function GET(request: NextRequest) {
  const { status, body } = await djangoFetch(request, 'GET');
  return NextResponse.json(body, { status });
}

export async function POST(request: NextRequest) {
  let parsed: unknown;
  try {
    parsed = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }
  const { status, body } = await djangoFetch(request, 'POST', parsed);
  return NextResponse.json(body, { status });
}

export async function PATCH(request: NextRequest) {
  let parsed: unknown;
  try {
    parsed = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }
  const { status, body } = await djangoFetch(request, 'PATCH', parsed);
  return NextResponse.json(body, { status });
}
