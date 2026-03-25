import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/isbn
 * ISBN 查詢代理端點
 *
 * 前端呼叫此端點，由後端統一處理：
 *   1. 驗證 ISBN 格式
 *   2. 先查本地 books 表
 *   3. 查不到才呼叫外部 Caves Books API
 *   4. 外部 API 有結果時寫入本地資料庫
 *
 * Request: { isbn: string }
 * Response: {
 *     success: boolean,
 *     error?: string,
 *     note?: string,
 *     data?: {
 *         isbn13?: string,
 *         isbn10?: string,
 *         title?: string,
 *         author?: string,
 *         publisher?: string,
 *         publication_year?: number | null,
 *         publication_date_text?: string | null,
 *         edition?: string | null,
 *         cover_image_url?: string | null,
 *     }
 * }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const isbn = (body.isbn || '').trim();

    console.log('[ISBN Proxy] 收到請求, isbn=', isbn);

    if (!isbn) {
      return NextResponse.json(
        {
          success: false,
          error: '請輸入 ISBN',
        },
        { status: 400 }
      );
    }

    // 直接呼叫後端 ISBN 查詢 API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    console.log('[ISBN Proxy] 呼叫後端, url=', `${backendUrl}/api/books/isbn/lookup/`);
    const backendResponse = await fetch(`${backendUrl}/api/books/isbn/lookup/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isbn }),
      // 傳遞 cookie 以維持 session
      credentials: 'include',
    });
    console.log('[ISBN Proxy] 後端回應, status=', backendResponse.status);

    const result = await backendResponse.json();
    console.log('[ISBN Proxy] 後端回應內容, result=', JSON.stringify(result));

    // 後端成功：本地或外部 API 有書
    if (result.success && result.data?.book) {
      const book = result.data.book;
      return NextResponse.json({
        success: true,
        data: {
          isbn13: book.isbn13,
          isbn10: book.isbn10 || undefined,
          title: book.title,
          author: book.author_display,
          publisher: book.publisher,
          publication_year: book.publication_year,
          publication_date_text: book.publication_date_text,
          edition: book.edition,
          cover_image_url: book.cover_image_url,
        },
        // 附加資訊（讓前端顯示查詢來源）
        _source: result.data.source,
        _message: result.data.message,
        _is_new: result.data.is_new,
      });
    }

    // 後端查無資料
    return NextResponse.json(
      {
        success: false,
        error: result.data?.message || '查無此 ISBN 之書籍資訊，請手動填寫',
        note: '可在書籍目錄、Google Books 或其他圖書網站查詢 ISBN 對應的書籍資訊',
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('[ISBN Proxy] Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: '無法連線書籍查詢服務，請稍後再試',
        note: '可在書籍目錄、Google Books 或其他圖書網站查詢 ISBN 對應的書籍資訊',
      },
      { status: 503 }
    );
  }
}
