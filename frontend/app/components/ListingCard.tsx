'use client';

import Link from 'next/link';

interface Book {
  id?: number;
  title: string;
  author_display?: string;
  author?: string;
  isbn13?: string;
  cover_image_url?: string;
}

interface Seller {
  id?: number;
  display_name?: string;
  department?: {
    id?: number;
    name_zh?: string;
  } | null;
}

interface ListingCardItem {
  id: number;
  book: Book;
  seller?: Seller;
  used_price: number;
  condition_level?: string;
  condition_level_display?: string;
  cover_image?: string;
  primary_image?: {
    file_path?: string;
    is_primary?: boolean;
  } | null;
}

export default function ListingCard({ listing }: { listing: ListingCardItem }) {
  // Build proper image URL - handle relative paths from backend
  let coverImage: string | null = null;

  // Priority 1: Direct cover_image
  if (listing.cover_image) {
    coverImage = listing.cover_image;
  }
  // Priority 2: Primary image from listings API
  else if (listing.primary_image?.file_path) {
    const filePath = listing.primary_image.file_path;
    // Check if it's already a full URL
    if (filePath.startsWith('http')) {
      coverImage = filePath;
    } else {
      // Build URL from relative path
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const backendUrl = API_BASE_URL.replace('/api', '');
      coverImage = `${backendUrl}/media/${filePath}`;
    }
  }
  // Priority 3: Book cover image
  else if (listing.book.cover_image_url) {
    coverImage = listing.book.cover_image_url;
  }

  // 作者信息
  const author = listing.book.author_display || listing.book.author || '作者未知';
  
  // 卖家系所显示
  const departmentDisplay = listing.seller?.department?.name_zh || '';

  return (
    <Link 
      href={`/listings/${listing.id}`} 
      style={{ textDecoration: 'none', color: 'inherit' }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '0.5rem',
          overflow: 'hidden',
          border: '1px solid #e9ecef',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          cursor: 'pointer',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
        onMouseEnter={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.transform = 'translateY(-8px)';
          el.style.boxShadow = '0 12px 24px rgba(30, 20, 10, 0.15)';
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.transform = 'translateY(0)';
          el.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        }}
      >
        {/* 封面圖像區 / Book Cover */}
        <div
          style={{
            height: '200px',
            backgroundColor: '#f9f7f2', // 浅灰色背景
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9b2335', // 印章紅
            fontSize: '3rem',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          {coverImage ? (
            <img
              src={coverImage}
              alt={listing.book.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              }}
              onMouseEnter={(e) => {
                const img = e.currentTarget as HTMLImageElement;
                img.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                const img = e.currentTarget as HTMLImageElement;
                img.style.transform = 'scale(1)';
              }}
            />
          ) : (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>📖</div>
              <div style={{ fontSize: '0.75rem', color: '#9b2335' }}>北商傳書</div>
            </div>
          )}
        </div>

        {/* 卡片主體 / Card Body */}
        <div style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* 書名 / Title */}
          <div
            style={{
              fontSize: '0.95rem',
              fontWeight: 600,
              color: '#1e140a', // 墨黑
              marginBottom: '0.25rem',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: '100%',
            }}
            title={listing.book.title}
          >
            {listing.book.title}
          </div>

          {/* 作者 / Author */}
          <div
            style={{
              fontSize: '0.85rem',
              color: '#6c757d', // 淡墨色
              marginBottom: '0.5rem',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={author}
          >
            {author}
          </div>

          {/* 系所標籤 / Department Badge (if available) */}
          {departmentDisplay && (
            <div
              style={{
                fontSize: '0.75rem',
                backgroundColor: '#f9f7f2', // 浅灰色
                color: '#9b2335', // 印章紅
                padding: '0.25rem 0.5rem',
                borderRadius: '0.25rem',
                marginBottom: '0.75rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              title={departmentDisplay}
            >
              {departmentDisplay}
            </div>
          )}

          {/* 價格與書況 / Price and Condition */}
          <div
            style={{
              marginTop: 'auto',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingTop: '0.5rem',
              borderTop: '1px solid #e9ecef',
            }}
          >
            {/* 價格 / Price */}
            <span
              style={{
                color: '#9b2335', // 印章紅
                fontWeight: 700,
                fontSize: '1.1rem',
              }}
            >
              NT${Math.ceil(parseFloat(String(listing.used_price)))}
            </span>

            {/* 書況 / Condition */}
            <span
              style={{
                backgroundColor: '#9b2335', // 印章紅
                color: '#ffffff', // 白色文字
                padding: '0.25rem 0.6rem',
                borderRadius: '0.25rem',
                fontSize: '0.75rem',
                fontWeight: 500,
                whiteSpace: 'nowrap',
              }}
            >
              {listing.condition_level_display || listing.condition_level || '普通'}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
