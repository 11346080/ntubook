'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
      <div className="text-center py-5">
        <h1 style={{ color: '#1A365D', fontSize: '2.5rem', fontWeight: 700 }}>
          歡迎來到 北商傳書
        </h1>
        <p style={{ color: '#475569', fontSize: '1.1rem', marginTop: '1rem' }}>
          輕鬆買賣二手教科書，讓知識流動
        </p>
        <div style={{ marginTop: '2rem' }}>
          <Link href="/listings" className="btn btn-primary" style={{ marginRight: '1rem' }}>
            瀏覽書籍
          </Link>
          <Link href="/accounts/login" className="btn btn-accent">
            登入
          </Link>
        </div>
      </div>

      {/* Featured Section */}
      <div className="row mt-5">
        <div className="col-md-4">
          <div style={{
            backgroundColor: '#FFFFFF',
            padding: '2rem',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
          }}>
            <i className="fas fa-book" style={{ fontSize: '2.5rem', color: '#1A365D' }}></i>
            <h5 style={{ marginTop: '1rem', color: '#1A365D' }}>豐富的書籍</h5>
            <p className="text-muted">超過千本教科書選擇</p>
          </div>
        </div>
        <div className="col-md-4">
          <div style={{
            backgroundColor: '#FFFFFF',
            padding: '2rem',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
          }}>
            <i className="fas fa-users" style={{ fontSize: '2.5rem', color: '#E67E22' }}></i>
            <h5 style={{ marginTop: '1rem', color: '#1A365D' }}>信任的社群</h5>
            <p className="text-muted">北商學生交易平台</p>
          </div>
        </div>
        <div className="col-md-4">
          <div style={{
            backgroundColor: '#FFFFFF',
            padding: '2rem',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
          }}>
            <i className="fas fa-shield-alt" style={{ fontSize: '2.5rem', color: '#10B981' }}></i>
            <h5 style={{ marginTop: '1rem', color: '#1A365D' }}>安全交易</h5>
            <p className="text-muted">保護買賣雙方權益</p>
          </div>
        </div>
      </div>
    </div>
  );
}

