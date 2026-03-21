'use client';

import Link from 'next/link';

interface Listing {
  id: number;
  book: {
    title: string;
    author: string;
  };
  used_price: number;
  condition_level?: string;
  condition_level_display?: string;
  cover_image?: string;
}

export default function ListingCard({ listing }: { listing: Listing }) {
  return (
    <Link href="/listings" style={{ textDecoration: 'none', color: 'inherit' }}>
      <div
        style={{
          border: '1px solid #e9ecef',
          borderRadius: '0.5rem',
          overflow: 'hidden',
          transition: 'box-shadow 0.2s',
          backgroundColor: 'white',
          cursor: 'pointer',
          display: 'block',
          textDecoration: 'none',
          height: '100%',
        }}
        onMouseEnter={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.boxShadow = '0 0.5rem 1rem rgba(0,0,0,0.1)';
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.boxShadow = '0 0 0 transparent';
        }}
      >
        {/* Book Image */}
        <div
          style={{
            height: '180px',
            backgroundColor: '#f8f9fa',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#adb5bd',
            fontSize: '3rem',
          }}
        >
          {listing.cover_image ? (
            <img
              src={listing.cover_image}
              alt={listing.book.title}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : (
            <i className="fas fa-book"></i>
          )}
        </div>

        {/* Card Body */}
        <div style={{ padding: '1rem' }}>
          {/* Title */}
          <div
            style={{
              fontSize: '0.95rem',
              fontWeight: 500,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              color: '#1a1a1a',
              marginBottom: '0.25rem',
            }}
            title={listing.book.title}
          >
            {listing.book.title}
          </div>

          {/* Author */}
          <div
            style={{
              color: '#6c757d',
              fontSize: '0.875rem',
              marginBottom: '0.5rem',
            }}
          >
            {listing.book.author || '作者未知'}
          </div>

          {/* Price and Condition */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span
              style={{
                color: '#0d6efd',
                fontWeight: 700,
                fontSize: '1.1rem',
              }}
            >
              NT${listing.used_price}
            </span>
            <span
              style={{
                backgroundColor: '#6c757d',
                color: 'white',
                padding: '0.25rem 0.5rem',
                borderRadius: '0.25rem',
                fontSize: '0.75rem',
                fontWeight: 500,
              }}
            >
              {listing.condition_level_display || listing.condition_level || '未知'}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
