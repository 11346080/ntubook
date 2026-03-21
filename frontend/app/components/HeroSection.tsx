'use client';

import Link from 'next/link';

interface HeroSectionProps {
  isAuthenticated?: boolean;
}

export default function HeroSection({ isAuthenticated = false }: HeroSectionProps) {
  return (
    <div
      style={{
        background: 'linear-gradient(135deg, #0d6efd 0%, #0d6efd99 100%)',
        color: 'white',
        padding: '4rem 0',
        borderRadius: '0.75rem',
        marginBottom: '2rem',
        textAlign: 'center',
      }}
    >
      <div className="container">
        <h1
          style={{
            marginBottom: '1rem',
            fontWeight: 700,
            fontSize: '2.5rem',
          }}
        >
          <i className="fas fa-book-open me-2"></i>歡迎來到北商傳書
        </h1>
        <p
          style={{
            marginBottom: '2rem',
            fontSize: '1.1rem',
            opacity: 0.9,
          }}
        >
          北商校內師生專屬的二手教科書媒合平台
        </p>
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '1.5rem',
            flexWrap: 'wrap',
          }}
        >
          <Link
            href="/listings"
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'white',
              color: '#0d6efd',
              textDecoration: 'none',
              borderRadius: '0.25rem',
              fontWeight: 500,
              fontSize: '1rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s',
              cursor: 'pointer',
            }}
            onMouseOver={(e) => {
              const target = e.currentTarget as HTMLElement;
              target.style.backgroundColor = '#f8f9fa';
            }}
            onMouseOut={(e) => {
              const target = e.currentTarget as HTMLElement;
              target.style.backgroundColor = 'white';
            }}
          >
            <i className="fas fa-search"></i>瀏覽書籍
          </Link>
          <Link
            href={isAuthenticated ? '/listings/create' : '/accounts/login'}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'transparent',
              color: 'white',
              textDecoration: 'none',
              border: '2px solid white',
              borderRadius: '0.25rem',
              fontWeight: 500,
              fontSize: '1rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s',
              cursor: 'pointer',
            }}
            onMouseOver={(e) => {
              const target = e.currentTarget as HTMLElement;
              target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            }}
            onMouseOut={(e) => {
              const target = e.currentTarget as HTMLElement;
              target.style.backgroundColor = 'transparent';
            }}
          >
            <i className="fas fa-plus"></i>我要賣書
          </Link>
        </div>
      </div>
    </div>
  );
}
