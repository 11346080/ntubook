'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface FilterFormProps {
  keyword: string;
  sort: string;
}

export default function FilterForm({ keyword: initialKeyword, sort: initialSort }: FilterFormProps) {
  const router = useRouter();
  const [keyword, setKeyword] = useState(initialKeyword);
  const [sort, setSort] = useState(initialSort);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (keyword.trim()) {
      params.append('keyword', keyword.trim());
    }
    if (sort) {
      params.append('sort', sort);
    }
    params.append('page', '1'); // 重新搜尋時重設為第一頁
    router.push(`/listings?${params.toString()}`);
  };

  const handleClear = () => {
    setKeyword('');
    setSort('-created_at');
    router.push('/listings');
  };

  return (
    <div
      style={{
        padding: '1.5rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '0.5rem',
        border: '1px solid #e9ecef',
      }}
    >
      <h6
        style={{
          marginBottom: '1.5rem',
          fontWeight: 600,
          color: '#1e140a',
          fontSize: '1rem',
        }}
      >
        <span style={{ color: '#9b2335', marginRight: '0.5rem' }}></span>
        進階篩選
      </h6>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* 關鍵字 / Keyword */}
        <div>
          <label
            htmlFor="keyword"
            style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '0.5rem',
              color: '#1e140a',
            }}
          >
            關鍵字
          </label>
          <input
            id="keyword"
            type="text"
            placeholder="書名、作者、ISBN..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderBottom: '2px solid transparent',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              color: '#1e140a',
              transition: 'border-color 0.3s ease',
              boxSizing: 'border-box',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderBottomColor = '#9b2335';
              e.currentTarget.style.outline = 'none';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderBottomColor = 'transparent';
            }}
          />
        </div>

        {/* 排序 / Sorting */}
        <div>
          <label
            htmlFor="sort"
            style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '0.5rem',
              color: '#1e140a',
            }}
          >
            排序方式
          </label>
          <select
            id="sort"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              color: '#1e140a',
              backgroundColor: 'white',
              cursor: 'pointer',
              transition: 'border-color 0.3s ease',
            }}
          >
            <option value="-created_at">最新上架</option>
            <option value="created_at">最舊上架</option>
            <option value="used_price">價格低到高</option>
            <option value="-used_price">價格高到低</option>
          </select>
        </div>

        {/* 提交按鈕 / Submit Button */}
        <button
          type="submit"
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#9b2335', // 印章紅
            color: '#f5edd8', // 宣紙白
            border: 'none',
            borderRadius: '0.25rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '0.9rem',
          }}
          onMouseEnter={(e) => {
            const btn = e.currentTarget as HTMLButtonElement;
            btn.style.backgroundColor = '#7a1a2b';
            btn.style.transform = 'translateY(-2px)';
            btn.style.boxShadow = '0 4px 12px rgba(155, 35, 53, 0.3)';
          }}
          onMouseLeave={(e) => {
            const btn = e.currentTarget as HTMLButtonElement;
            btn.style.backgroundColor = '#9b2335';
            btn.style.transform = 'translateY(0)';
            btn.style.boxShadow = 'none';
          }}
        >
          執行搜尋
        </button>

        {/* 清除篩選 / Clear Filters */}
        {(keyword || sort !== '-created_at') && (
          <button
            type="button"
            onClick={handleClear}
            style={{
              width: '100%',
              padding: '0.75rem',
              color: '#9b2335', // 印章紅
              backgroundColor: 'transparent',
              border: '1px solid #9b2335',
              borderRadius: '0.25rem',
              fontWeight: 500,
              cursor: 'pointer',
              fontSize: '0.875rem',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.backgroundColor = 'rgba(155, 35, 53, 0.08)';
            }}
            onMouseLeave={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.backgroundColor = 'transparent';
            }}
          >
            清除篩選
          </button>
        )}
      </form>
    </div>
  );
}
