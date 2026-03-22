import { NextRequest, NextResponse } from 'next/server';

interface CavesBookResponse {
  status: number;
  msg: string;
  data?: {
    title?: string;
    author?: string;
    publisher?: string;
    isbn?: string;
    [key: string]: any;
  }[];
}

interface BookData {
  title: string;
  author: string;
  publisher: string;
  isbn13?: string;
  isbn10?: string;
}

/** 
 * POST /api/isbn
 * 通过 ISBN 查询书籍信息 (调用 Caves Books API)
 * Request: { isbn: string }
 * Response: { success: boolean, data?: BookData, error?: string }
 */
export async function POST(request: NextRequest) {
  // Simple fallback - ISBN lookup disabled due to external API issues
  // User can manually fill in book information
  return NextResponse.json({
    success: false,
    error: '暫無法自動查詢 ISBN,請手動填入書籍資訊',
    note: '可在豆瓣、Google Books 或其他圖書網站查詢 ISBN 對應的書籍資訊',
  }, { status: 503 });
}
