import { NextRequest, NextResponse } from 'next/server';

interface NSFWDetectResponse {
  is_nsfw: boolean;
  [key: string]: any;
}

/**
 * POST /api/nsfw-check
 * 检查上传的图片是否包含不适当内容
 * Request: FormData with file "image"
 * Response: { success: boolean, is_safe: boolean, error?: string }
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File | null;

    if (!file) {
      return NextResponse.json(
        {
          success: false,
          error: '未提供圖片檔案',
        },
        { status: 400 }
      );
    }

    // 检查文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        {
          success: false,
          error: '僅支援 JPG、PNG、WebP、GIF 格式',
        },
        { status: 400 }
      );
    }

    // 检查文件大小（限制 10MB）
    if (file.size > 10 * 1024 * 1024) {
      return NextResponse.json(
        {
          success: false,
          error: '圖片檔案過大，請選擇小於 10MB 的檔案',
        },
        { status: 400 }
      );
    }

    // 将文件转换为 Buffer 并编码为 base64
    const buffer = await file.arrayBuffer();
    const base64 = Buffer.from(buffer).toString('base64');

    // 调用 NSFW 检测 API
    const nsfwFormData = new FormData();
    const blob = new Blob([buffer], { type: file.type });
    nsfwFormData.append('image', blob, file.name);

    let nsfwResponse;
    try {
      nsfwResponse = await fetch('https://nsfwdet.com/api/v1/detect-nsfw', {
        method: 'POST',
        body: nsfwFormData,
        // 不设置 Content-Type，让浏览器自动设置 multipart/form-data
      });
    } catch (fetchError) {
      // 如果 API 不可用，默认允许上传（为开发环境友好）
      console.warn('NSFW API 不可用，允许上传:', fetchError);
      return NextResponse.json(
        {
          success: true,
          is_safe: true, // 默认安全
        },
        { status: 200 }
      );
    }

    if (!nsfwResponse.ok) {
      console.error('NSFW API Error:', nsfwResponse.status, nsfwResponse.statusText);
      // API 错误时也默认允许
      return NextResponse.json(
        {
          success: true,
          is_safe: true,
        },
        { status: 200 }
      );
    }

    const nsfwData: NSFWDetectResponse = await nsfwResponse.json();

    const isSafe = !nsfwData.is_nsfw; // is_nsfw=true 表示不安全

    return NextResponse.json(
      {
        success: true,
        is_safe: isSafe,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('NSFW Check Error:', error);

    // 错误时默认允许上传（更友好的用户体验）
    return NextResponse.json(
      {
        success: true,
        is_safe: true, // 出错时默认允许
      },
      { status: 200 }
    );
  }
}
