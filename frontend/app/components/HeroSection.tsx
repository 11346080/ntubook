'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface HeroSectionProps {
  isAuthenticated?: boolean;
}

export default function HeroSection({ isAuthenticated = false }: HeroSectionProps) {
  const [keyword, setKeyword] = useState('');
  const router = useRouter();

  const handleSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (keyword.trim()) {
      router.push(`/listings?keyword=${encodeURIComponent(keyword.trim())}`);
    }
  };

  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && keyword.trim()) {
      router.push(`/listings?keyword=${encodeURIComponent(keyword.trim())}`);
    }
  };

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

        {/* 搜尋框 - 東方美學設計 */}
        <form
          onSubmit={handleSearchSubmit}
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '0.5rem',
            marginBottom: '2rem',
            maxWidth: '600px',
            margin: '0 auto 2rem auto',
          }}
        >
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyPress={handleSearchKeyPress}
            placeholder="搜尋書名、作者、ISBN..."
            style={{
              flex: 1,
              padding: '0.75rem 1rem',
              border: 'none',
              borderBottom: '2px solid rgba(255, 255, 255, 0.5)',
              backgroundColor: 'transparent',
              color: 'white',
              fontSize: '1rem',
              outline: 'none',
              transition: 'border-color 0.3s ease',
              minWidth: '200px',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderBottomColor = '#9b2335';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderBottomColor = 'rgba(255, 255, 255, 0.5)';
            }}
          />
          <button
            type="submit"
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#9b2335',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              fontWeight: 500,
              fontSize: '1rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              whiteSpace: 'nowrap',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#7a1a2b';
              e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#9b2335';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <i className="fas fa-search"></i>搜尋
          </button>
        </form>

        {/* 快速操作按鈕區 */}
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
            <i className="fas fa-list"></i>瀏覽書籍
          </Link>
          <Link
            href="/accounts/login"
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

      <style>{`
        input::placeholder {
          color: rgba(255, 255, 255, 0.7);
        }
      `}</style>
    </div>
  );
}
