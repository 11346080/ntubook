import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const djangoApiBase = (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/api\/?$/, '');
  const fetchUrl = `${djangoApiBase}/api/accounts/me/`;

  const appToken = request.cookies.get('app_token')?.value;

  if (!appToken) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const response = await fetch(fetchUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-App-Token': appToken,
      },
    });

    const rawText = await response.text();
    let data: unknown;
    try {
      data = JSON.parse(rawText);
    } catch {
      return NextResponse.json({ error: 'Backend unreachable', raw: rawText.slice(0, 200) }, { status: 502 });
    }

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 502 });
  }
}
