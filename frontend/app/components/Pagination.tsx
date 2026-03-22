'use client';

import { CSSProperties } from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  // 計算顯示的頁碼 / Calculate page numbers to display
  const maxPagesToShow = 5;
  const startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
  const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
  const adjustedStartPage = Math.max(1, endPage - maxPagesToShow + 1);

  const pageNumbers = Array.from(
    { length: endPage - adjustedStartPage + 1 },
    (_, i) => adjustedStartPage + i
  );

  const buttonStyle = (isActive: boolean) => ({
    backgroundColor: isActive ? '#9b2335' : 'white',
    color: isActive ? 'white' : '#1e140a',
    border: isActive ? 'none' : '1px solid #e9ecef',
    padding: '0.5rem 0.75rem',
    borderRadius: '0.25rem',
    cursor: isActive ? 'default' : 'pointer',
    fontSize: '0.875rem',
    fontWeight: isActive ? 600 : 500,
    transition: 'all 0.3s ease',
  });

  const navStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '0.25rem',
    marginTop: '2rem',
    flexWrap: 'wrap',
  };

  return (
    <nav aria-label="Page navigation" style={navStyle}>
      {/* 上一頁 / Previous Button */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={{
          ...buttonStyle(false),
          backgroundColor: currentPage === 1 ? '#f8f9fa' : 'white',
          color: currentPage === 1 ? '#adb5bd' : '#1e140a',
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
          border: '1px solid #e9ecef',
        }}
        onMouseEnter={(e) => {
          if (currentPage > 1) {
            const el = e.currentTarget as HTMLButtonElement;
            el.style.backgroundColor = '#f5edd8';
            el.style.borderColor = '#9b2335';
          }
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLButtonElement;
          el.style.backgroundColor = 'white';
          el.style.borderColor = '#e9ecef';
        }}
      >
        ← 上一頁
      </button>

      {/* First page if not visible */}
      {adjustedStartPage > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            style={buttonStyle(false)}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = '#f5edd8';
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = 'white';
            }}
          >
            1
          </button>
          {adjustedStartPage > 2 && (
            <span style={{ color: '#6c757d', padding: '0.5rem 0.25rem' }}>...</span>
          )}
        </>
      )}

      {/* 頁碼 / Page Numbers */}
      {pageNumbers.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          style={buttonStyle(page === currentPage)}
          onMouseEnter={(e) => {
            if (page !== currentPage) {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = '#f5edd8';
              el.style.borderColor = '#9b2335';
            }
          }}
          onMouseLeave={(e) => {
            if (page !== currentPage) {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = 'white';
              el.style.borderColor = '#e9ecef';
            }
          }}
        >
          {page}
        </button>
      ))}

      {/* Last page if not visible */}
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && (
            <span style={{ color: '#6c757d', padding: '0.5rem 0.25rem' }}>...</span>
          )}
          <button
            onClick={() => onPageChange(totalPages)}
            style={buttonStyle(false)}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = '#f5edd8';
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLButtonElement;
              el.style.backgroundColor = 'white';
            }}
          >
            {totalPages}
          </button>
        </>
      )}

      {/* 下一頁 / Next Button */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={{
          ...buttonStyle(false),
          backgroundColor: currentPage === totalPages ? '#f8f9fa' : 'white',
          color: currentPage === totalPages ? '#adb5bd' : '#1e140a',
          cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
          border: '1px solid #e9ecef',
        }}
        onMouseEnter={(e) => {
          if (currentPage < totalPages) {
            const el = e.currentTarget as HTMLButtonElement;
            el.style.backgroundColor = '#f5edd8';
            el.style.borderColor = '#9b2335';
          }
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLButtonElement;
          el.style.backgroundColor = 'white';
          el.style.borderColor = '#e9ecef';
        }}
      >
        下一頁 →
      </button>
    </nav>
  );
}
