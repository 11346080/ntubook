'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ListingCard from './ListingCard';
import Pagination from './Pagination';

interface Book {
  id: number;
  title: string;
  author_display: string;
  isbn13: string;
  isbn10?: string;
  cover_image_url?: string;
}

interface Seller {
  id: number;
  display_name?: string;
  department?: {
    id: number;
    name_zh: string;
  } | null;
}

interface ListingImage {
  id: number;
  image_base64: string | null;  // base64 data URL (data:image/jpeg;base64,...)
  mime_type: string;
  file_name: string;
  is_primary: boolean;
  sort_order: number;
}

interface Listing {
  id: number;
  book: Book;
  seller?: Seller;
  used_price: string | number;
  condition_level: string;
  condition_level_display: string;
  description?: string;
  seller_note?: string;
  primary_image?: ListingImage | null;
  created_at: string;
  updated_at?: string;
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Listing[];
}

interface SearchResultsContentProps {
  keyword: string;
  sort: string;
  program_type_id?: string;
  department_id?: string;
  grade_no?: string;
}

export default function SearchResultsContent({
  keyword,
  sort,
  program_type_id,
  department_id,
  grade_no,
}: SearchResultsContentProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    count: 0,
    totalPages: 1,
    currentPage: 1,
  });

  useEffect(() => {
    const fetchListings = async () => {
      setLoading(true);
      setError(null);
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const params = new URLSearchParams();
        if (keyword) {
          params.append('keyword', keyword);
        }
        if (program_type_id) {
          params.append('program_type_id', program_type_id);
        }
        if (department_id) {
          params.append('department_id', department_id);
        }
        if (grade_no) {
          params.append('grade_no', grade_no);
        }
        if (sort) {
          params.append('sort', sort);
        }
        params.append('page', currentPage.toString());
        params.append('page_size', '24');

        const url = `${API_BASE_URL}/listings/?${params.toString()}`;
        const response = await fetch(url, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data: ApiResponse = await response.json();
        const listingsArray = data.results || [];
        const totalCount = data.count || 0;
        const totalPages = Math.ceil(totalCount / 24);

        setListings(listingsArray);
        setPagination({
          count: totalCount,
          totalPages,
          currentPage,
        });
      } catch (err) {
        // Error fetching listings
        setError(
          err instanceof Error
            ? err.message
            : '無法載入書籍資訊，請稍後重試'
        );
        setListings([]);
        setPagination({
          count: 0,
          totalPages: 1,
          currentPage: 1,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, [keyword, sort, program_type_id, department_id, grade_no, currentPage]);

  const handlePageChange = (page: number) => {
    const newParams = new URLSearchParams(searchParams.toString());
    newParams.set('page', page.toString());
    router.push(`/listings?${newParams.toString()}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div
          style={{
            display: 'inline-block',
            width: '2rem',
            height: '2rem',
            border: '3px solid rgba(155, 35, 53, 0.3)',
            borderTop: '3px solid #9b2335',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <p style={{ marginTop: '1rem', color: '#6c757d' }}>載入中...</p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: '2rem',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '0.5rem',
          color: '#856404',
          textAlign: 'center',
        }}
      >
        <i className="fas fa-exclamation-triangle me-2"></i>
        {error}
      </div>
    );
  }

  // 空状態: 搜尋結果為空
  if (listings.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem', color: '#adb5bd' }}>
          
        </div>
        <p
          style={{
            fontSize: '1.25rem',
            color: '#6c757d',
            marginBottom: '0.5rem',
            fontWeight: 500,
          }}
        >
          {keyword
            ? '墨跡未乾，暫無符合條件之藏書...'
            : '暫無書籍上架'}
        </p>
        {keyword && (
          <p style={{ fontSize: '0.9rem', color: '#adb5bd', marginBottom: 0 }}>
            試試看修改搜尋條件或瀏覽全部書籍
          </p>
        )}
      </div>
    );
  }

  // 正常顯示結果
  return (
    <>
      {/* 結果摘要 / Results Summary */}
      <div
        style={{
          marginBottom: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          marginTop: '4rem',
        }}
      >
        <span style={{ fontSize: '0.9rem', color: '#6c757d' }}>
          共 <strong style={{ color: '#1e140a' }}>{pagination.count}</strong> 本書籍
          {pagination.totalPages > 1 && (
            <>
              ，第 <strong style={{ color: '#1e140a' }}>{pagination.currentPage}</strong> 頁
            </>
          )}
        </span>
      </div>

      {/* 書籍網格 / Listings Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        {listings.map((listing) => (
          <ListingCard
            key={listing.id}
            listing={{
              id: listing.id,
              book: {
                title: listing.book.title,
                author_display: listing.book.author_display,
                author: listing.book.author_display,
                isbn13: listing.book.isbn13,
                cover_image_url: listing.book.cover_image_url,
              },
              seller: listing.seller,
              used_price: typeof listing.used_price === 'string' ? parseFloat(listing.used_price) : listing.used_price,
              condition_level: listing.condition_level,
              condition_level_display: listing.condition_level_display,
              primary_image: listing.primary_image,
            }}
          />
        ))}
      </div>

      {/* 分頁控制 / Pagination */}
      {pagination.totalPages > 1 && (
        <Pagination
          currentPage={pagination.currentPage}
          totalPages={pagination.totalPages}
          onPageChange={handlePageChange}
        />
      )}
    </>
  );
}
