'use client';

import Link from 'next/link';
import HeroSection from './components/HeroSection';
import ListingCard from './components/ListingCard';

/**
 * Mock 書籍資料 - 與 Django Model 欄位對應
 */
const MOCK_LISTINGS = [
  {
    id: 1,
    book: { title: 'Python 從入門到精通', author: 'Mark Lutz' },
    used_price: 450,
    condition_level: 'excellent',
    condition_level_display: '優良',
    cover_image: '',
  },
  {
    id: 2,
    book: { title: '資料結構與演算法', author: 'Thomas H. Cormen' },
    used_price: 580,
    condition_level: 'good',
    condition_level_display: '良好',
    cover_image: '',
  },
  {
    id: 3,
    book: { title: '計算機組織與設計', author: 'David Patterson' },
    used_price: 520,
    condition_level: 'fair',
    condition_level_display: '中等',
    cover_image: '',
  },
  {
    id: 4,
    book: { title: '微積分', author: 'James Stewart' },
    used_price: 380,
    condition_level: 'excellent',
    condition_level_display: '優良',
    cover_image: '',
  },
];

const isAuthenticated = false; // TODO: 從認證狀態取得

export default function Home() {
  return (
    <main style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
      <div className="container">
        {/* 1. Hero Section */}
        <HeroSection isAuthenticated={isAuthenticated} />

        {/* 2. 最新上架區塊 */}
        <section style={{ marginBottom: '4rem' }}>
          <h2
            style={{
              fontWeight: 700,
              marginBottom: '1.5rem',
              borderLeft: '4px solid #0d6efd',
              paddingLeft: '0.75rem',
              fontSize: '1.5rem',
              color: '#1A365D'
            }}
          >
            <i className="fas fa-clock me-2"></i>最新上架
          </h2>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {MOCK_LISTINGS.map((listing) => (
              <div key={listing.id}>
                <ListingCard listing={listing} />
              </div>
            ))}
          </div>

          {/* 查看更多按鈕 */}
          <div style={{ textAlign: 'right', marginTop: '2rem' }}>
            <Link
              href="/listings"
              className="btn btn-outline-primary"
              style={{
                borderRadius: '0.25rem',
                fontWeight: 500,
              }}
            >
              看更多書籍 <i className="fas fa-arrow-right ms-1"></i>
            </Link>
          </div>
        </section>

        {/* 3. 特色介紹區塊 (修正後的區塊) */}
        <div className="row g-4 mb-5">
          <div className="col-md-4">
            <div style={featureCardStyle}>
              <i className="fas fa-book" style={{ fontSize: '2.5rem', color: '#0d6efd' }}></i>
              <h5 style={{ marginTop: '1rem', color: '#1A365D', fontWeight: 700 }}>豐富的書籍</h5>
              <p className="text-muted">超過千本教科書選擇</p>
            </div>
          </div>
          <div className="col-md-4">
            <div style={featureCardStyle}>
              <i className="fas fa-users" style={{ fontSize: '2.5rem', color: '#F59E0B' }}></i>
              <h5 style={{ marginTop: '1rem', color: '#1A365D', fontWeight: 700 }}>信任的社群</h5>
              <p className="text-muted">北商學生專屬交易平台</p>
            </div>
          </div>
          <div className="col-md-4">
            <div style={featureCardStyle}>
              <i className="fas fa-shield-alt" style={{ fontSize: '2.5rem', color: '#10B981' }}></i>
              <h5 style={{ marginTop: '1rem', color: '#1A365D', fontWeight: 700 }}>安全交易</h5>
              <p className="text-muted">保護買賣雙方權益</p>
            </div>
          </div>
        </div>

        {/* 4. 熱門書籍 (即將上線) */}
        <section>
          <h2 style={{
              fontWeight: 700,
              marginBottom: '1.5rem',
              borderLeft: '4px solid #0d6efd',
              paddingLeft: '0.75rem',
              fontSize: '1.5rem',
              color: '#1A365D'
          }}>
            <i className="fas fa-fire me-2"></i>熱門書籍
          </h2>
          <div style={{
              backgroundColor: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '0.5rem',
              padding: '2rem',
              textAlign: 'center',
              color: '#6c757d',
          }}>
            <i className="fas fa-info-circle me-2"></i>
            熱門書籍模組即將上線，敬請期待。
          </div>
        </section>
      </div>
    </main>
  );
}

// 抽取重複的樣式
const featureCardStyle = {
  backgroundColor: '#FFFFFF',
  padding: '2rem',
  borderRadius: '12px',
  textAlign: 'center' as const,
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
  height: '100%',
  border: '1px solid #f0f0f0'
};