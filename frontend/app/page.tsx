'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import '@/app/style/homepage.css';

// ── 水墨滴資料結構 ──────────────────────────────────────────────
interface InkBlob {
  x: number;
  y: number;
  born: number;
  life: number;
  coreR: number;       // 最終半徑
  seed: number;
  blobOffsets: number[]; // 16 點不規則邊緣偏移
  tendrils: { angle: number; len: number; width: number }[];
}

function createBlob(x: number, y: number, fast: boolean): InkBlob {
  const base = fast ? 10 + Math.random() * 8 : 6 + Math.random() * 6;
  return {
    x,
    y,
    born: performance.now(),
    life: 1200 + Math.random() * 500,
    coreR: base,
    seed: Math.random() * 100,
    blobOffsets: Array.from({ length: 16 }, () => 0.82 + Math.random() * 0.36),
    tendrils: Array.from({ length: fast ? 5 : 2 }, () => ({
      angle: Math.random() * Math.PI * 2,
      len: base * (0.6 + Math.random() * 0.8),
      width: 1 + Math.random() * 2,
    })),
  };
}

function drawBlob(
  ctx: CanvasRenderingContext2D,
  blob: InkBlob,
  timestamp: number
) {
  const age = timestamp - blob.born;
  const p = Math.min(age / blob.life, 1);
  if (p >= 1) return;

  // 前 20% 快速展開，之後固定形狀
  const growP = Math.min(p / 0.2, 1);
  // 60% 後才開始淡出，快速消失
  const fadeP = Math.pow(Math.max((p - 0.1) / 0.6, 0), 2.2);
  // 整體不透明度高（0.82），讓墨水看起來濃黑
  const alpha = (1 - fadeP) * 0.3;
  if (alpha < 0.02) return;

  const r = blob.coreR * (0.3 + growP * 0.7); // 從 30% 大小展開到 100%
  if (!isFinite(r) || r <= 0) return;

  const cx = blob.x;
  const cy = blob.y;
  const BLOB_POINTS = 16;

  try {
    ctx.save();

    // ── 1. 主墨滴：不規則多邊形 + 濃黑漸層 ──────────────────
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    for (let i = 0; i <= BLOB_POINTS; i++) {
      const idx = i % BLOB_POINTS;
      const angle = (idx / BLOB_POINTS) * Math.PI * 2;
      const wobble = blob.blobOffsets[idx] ?? 1;
      const bx = cx + Math.cos(angle) * r * wobble;
      const by = cy + Math.sin(angle) * r * wobble;
      if (i === 0) {
        ctx.moveTo(bx, by);
      } else {
        ctx.lineTo(bx, by);
      }
    }
    ctx.closePath();

    // 墨水漸層：純黑核心，邊緣快速衰減到透明
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 1.1);
    g.addColorStop(0,   `rgba(5,3,1,1)`);
    g.addColorStop(0.4, `rgba(8,5,2,0.95)`);
    g.addColorStop(0.72,`rgba(18,12,5,0.7)`);
    g.addColorStop(0.9, `rgba(28,18,8,0.25)`);
    g.addColorStop(1,   `rgba(35,22,8,0)`);
    ctx.fillStyle = g;
    ctx.fill();

    // ── 2. 極窄暈染邊（只有 1.4 倍半徑，保持銳利）────────────
    const hazeR = r * 1.4;
    const haze = ctx.createRadialGradient(cx, cy, r * 0.6, cx, cy, hazeR);
    haze.addColorStop(0, `rgba(10,6,2,${0.18 * alpha})`);
    haze.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.arc(cx, cy, hazeR, 0, Math.PI * 2);
    ctx.fillStyle = haze;
    ctx.fill();

    ctx.restore();

    // ── 3. 觸鬚：細線＋末端小墨珠 ───────────────────────────
    if (growP > 0.3) {
      ctx.save();
      ctx.globalAlpha = alpha * 0.75;
      blob.tendrils.forEach(t => {
        const tx = cx + Math.cos(t.angle) * t.len * growP;
        const ty = cy + Math.sin(t.angle) * t.len * growP;

        // 觸鬚線
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(t.angle) * r * 0.8, cy + Math.sin(t.angle) * r * 0.8);
        ctx.lineTo(tx, ty);
        ctx.strokeStyle = `rgba(6,3,1,${alpha * 0.85})`;
        ctx.lineWidth = t.width * (1 - p * 0.5);
        ctx.lineCap = 'round';
        ctx.stroke();

        // 末端墨珠
        const tipR = t.width * 1.5;
        if (tipR > 0) {
          const tipG = ctx.createRadialGradient(tx, ty, 0, tx, ty, tipR * 2);
          tipG.addColorStop(0, `rgba(8,5,2,${alpha * 0.7})`);
          tipG.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.beginPath();
          ctx.arc(tx, ty, tipR * 2, 0, Math.PI * 2);
          ctx.fillStyle = tipG;
          ctx.fill();
        }
      });
      ctx.restore();
    }
  } catch {
    // 靜默捕捉
  }
}

// ── 首頁推薦書籍卡片 ──────────────────────────────────────────────
interface Listing {
  id: number;
  book_title: string;
  book_author: string;
  cover_image_url: string | null;
  used_price: number;
  condition_level: string;
  seller_display_name: string;
  seller_department: string | null;
  created_at: string;
  primary_image: {
    id: number;
    file_path: string;
    is_primary: boolean;
    sort_order: number;
  } | null;
}

function LatestListingCard({ listing }: { listing: Listing }) {
  // Build proper image URL - handle relative paths from backend
  let imageUrl: string | null = null;

  // Priority 1: Primary image from API (with URL construction)
  if (listing.primary_image?.file_path) {
    const filePath = listing.primary_image.file_path;
    // Check if it's already a full URL
    if (filePath.startsWith('http')) {
      imageUrl = filePath;
    } else {
      // Build URL from relative path
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      imageUrl = `${API_BASE_URL}/media/${filePath}`;
    }
  }
  // Priority 2: Book cover image
  else if (listing.cover_image_url) {
    imageUrl = listing.cover_image_url;
  }

  return (
    <Link href={`/listings/${listing.id}`} style={{ textDecoration: 'none' }}>
      <div
        style={{
          borderRadius: 'var(--border-radius)',
          overflow: 'hidden',
          backgroundColor: 'var(--color-bg-primary)',
          border: `1px solid var(--color-border)`,
          transition: 'all var(--transition-duration) ease',
          cursor: 'pointer',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        }}
        onMouseEnter={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.transform = 'translateY(-4px)';
          el.style.boxShadow = '0 8px 16px rgba(155, 35, 53, 0.15)';
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.transform = 'translateY(0)';
          el.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)';
        }}
      >
        {/* 封面圖 */}
        <div
          style={{
            height: '200px',
            backgroundColor: 'var(--color-bg-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={listing.book_title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          ) : null}
          {!imageUrl && (
            <div
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '48px',
                color: 'var(--color-muted)',
              }}
            >
              <i className="fas fa-book"></i>
            </div>
          )}
        </div>

        {/* 卡片內容 */}
        <div style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* 書名 */}
          <h6
            style={{
              fontFamily: "'Noto Serif TC', serif",
              fontSize: '16px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              margin: '0 0 0.5rem 0',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={listing.book_title}
          >
            {listing.book_title}
          </h6>

          {/* 作者 */}
          <p
            style={{
              fontSize: '13px',
              color: 'var(--color-text-secondary)',
              margin: '0 0 0.75rem 0',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={listing.book_author}
          >
            {listing.book_author}
          </p>

          {/* 賣家資訊 */}
          <p
            style={{
              fontSize: '12px',
              color: 'var(--color-muted)',
              margin: '0 0 0.75rem 0',
            }}
          >
            <i className="fas fa-user-circle me-1" style={{ color: 'var(--color-seal)' }}></i>
            {listing.seller_display_name}
            {listing.seller_department && ` · ${listing.seller_department}`}
          </p>

          {/* 價格 & 狀況 */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingTop: '0.75rem',
              borderTop: `1px solid var(--color-border)`,
              marginTop: 'auto',
            }}
          >
            <span
              style={{
                fontSize: '18px',
                fontWeight: '700',
                color: 'var(--color-seal)',
              }}
            >
              $NT {listing.used_price.toLocaleString()}
            </span>
            <span
              style={{
                fontSize: '12px',
                backgroundColor: 'var(--color-bg-light)',
                color: 'var(--color-text-secondary)',
                padding: '0.35rem 0.6rem',
                borderRadius: 'calc(var(--border-radius) / 2)',
              }}
            >
              {getConditionLabel(listing.condition_level)}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

function getConditionLabel(level: string): string {
  const labels: { [key: string]: string } = {
    LIKE_NEW: '幾全新',
    GOOD: '良好',
    FAIR: '普通',
    POOR: '較差',
  };
  return labels[level] || level;
}

// ── 最新上架區塊 ──────────────────────────────────────────────────
function RecommendedListingsSection() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendedListings = async () => {
      try {
        setLoading(true);
        // 可改用推薦排序 API，如果後端有的話；否則用最新 API 取前 8 本
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        const response = await fetch(`${API_BASE_URL}/api/listings/latest/`);
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.statusText}`);
        }
        const data = await response.json();
        setListings(Array.isArray(data.data) ? data.data : data.data?.results || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching recommended listings:', err);
        setError('無法載入推薦書籍');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendedListings();
  }, []);

  if (error) {
    return (
      <section style={{ padding: '4rem 0', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-muted)' }}>{error}</p>
      </section>
    );
  }

  return (
    <section style={{ padding: '4rem 0' }}>
      {/* 標題 */}
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h2
          style={{
            fontFamily: "'Noto Serif TC', serif",
            fontSize: '32px',
            fontWeight: '700',
            color: 'var(--color-text-primary)',
            marginBottom: '0.5rem',
          }}
        >
          推薦書籍
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '16px' }}>
          跟你修同一門課的人都在用 - 傳承書單
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner-border" style={{ color: 'var(--color-seal)' }} role="status">
            <span className="visually-hidden">載入中...</span>
          </div>
        </div>
      ) : listings.length > 0 ? (
        <>
          {/* 書籍網格 - 使用 CSS 限制數量 */}
          <div
            className="recommended-listings-grid"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem',
            }}
          >
            {listings.map((listing) => (
              <LatestListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}

// ── 最新上架區塊 ──────────────────────────────────────────────────
function LatestListingsSection() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLatestListings = async () => {
      try {
        setLoading(true);
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        const response = await fetch(`${API_BASE_URL}/api/listings/latest/`);
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.statusText}`);
        }
        const data = await response.json();
        setListings(Array.isArray(data.data) ? data.data : data.data?.results || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching listings:', err);
        setError('無法載入最新書籍');
      } finally {
        setLoading(false);
      }
    };

    fetchLatestListings();
  }, []);

  if (error) {
    return (
      <section style={{ padding: '4rem 0', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-muted)' }}>{error}</p>
      </section>
    );
  }

  return (
    <section style={{ padding: '4rem 0' }}>
      {/* 標題 */}
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h2
          style={{
            fontFamily: "'Noto Serif TC', serif",
            fontSize: '32px',
            fontWeight: '700',
            color: 'var(--color-text-primary)',
            marginBottom: '0.5rem',
          }}
        >
          最新上架
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '16px' }}>
          發現最新的二手好書
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner-border" style={{ color: 'var(--color-seal)' }} role="status">
            <span className="visually-hidden">載入中...</span>
          </div>
        </div>
      ) : listings.length > 0 ? (
        <>
          {/* 書籍網格 - 使用 CSS 限制數量 */}
          <div
            className="latest-listings-grid"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem',
            }}
          >
            {listings.map((listing) => (
              <LatestListingCard key={listing.id} listing={listing} />
            ))}
          </div>

          {/* 查看全部按鈕 */}
          <div style={{ textAlign: 'center' }}>
            <Link
              href="/listings?ordering=-created_at"
              className="browse-all-btn"
            >
              <span>瀏覽全部書籍</span>
              <i className="fas fa-arrow-right"></i>
            </Link>
          </div>
        </>
      ) : null}
    </section>
  );
}

// ── 主元件 ────────────────────────────────────────────────────────
export default function HomePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const blobsRef = useRef<InkBlob[]>([]);
  const animFrameRef = useRef<number>(0);
  const lastPosRef = useRef<{ x: number; y: number } | null>(null);
  const lastTimeRef = useRef<number>(0);

  const [showContent, setShowContent] = useState(false);
  const [introPhase, setIntroPhase] = useState<'logo' | 'expand' | 'done'>('logo');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [condition, setCondition] = useState('');

  useEffect(() => {
    const t1 = setTimeout(() => setIntroPhase('expand'), 1600);
    const t2 = setTimeout(() => {
      setIntroPhase('done');
      setShowContent(true);
    }, 2800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const draw = (ts: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.globalCompositeOperation = 'source-over';
      blobsRef.current = blobsRef.current.filter(b => ts - b.born < b.life);
      for (const blob of blobsRef.current) drawBlob(ctx, blob, ts);
      animFrameRef.current = requestAnimationFrame(draw);
    };
    animFrameRef.current = requestAnimationFrame(draw);

    const handleMouseMove = (e: MouseEvent) => {
      const now = performance.now();
      const last = lastPosRef.current;
      let fast = false;

      if (last) {
        const dx = e.clientX - last.x;
        const dy = e.clientY - last.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const dt = now - lastTimeRef.current;
        // 距離門檻 5px：確保相鄰墨滴有重疊（coreR 約 6~18px）
        if (dist < 5 || dt < 14) return;
        fast = dist / dt > 1.2; // 快速移動 → 較大墨滴
      }

      lastPosRef.current = { x: e.clientX, y: e.clientY };
      lastTimeRef.current = now;

      if (blobsRef.current.length < 90) {
        blobsRef.current.push(createBlob(e.clientX, e.clientY, fast));
      }
    };

    const handleClick = (e: MouseEvent) => {
      // 點擊爆出 5 個大墨滴，模擬濃墨落下
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          blobsRef.current.push(
            createBlob(
              e.clientX + (Math.random() - 0.5) * 20,
              e.clientY + (Math.random() - 0.5) * 20,
              true
            )
          );
        }, i * 40);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('click', handleClick);

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('click', handleClick);
      cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (category) params.set('category', category);
    if (condition) params.set('condition', condition);
    // 導航到書籍列表頁面（/listings 是現有的頁面）
    window.location.href = params.toString() ? `/listings?${params.toString()}` : '/listings';
  };

  return (
    <div className="homepage-body-override">
      <canvas ref={canvasRef} id="ink-canvas" />

      {introPhase !== 'done' && (
        <div className={`intro-overlay ${introPhase === 'expand' ? 'fade-out' : ''}`}>
          <Image
            className={`intro-logo-img ${introPhase === 'expand' ? 'shrink' : ''}`}
            src="/images/Logo.png"
            alt="北商傳書"
            width={300}
            height={220}
            style={{ width: 'auto', height: '200px', objectFit: 'contain', mixBlendMode: 'multiply' }}
            priority
          />
        </div>
      )}

      <div className="ink-frame" />
      <div className="corner corner-tl" />
      <div className="corner corner-tr" />
      <div className="corner corner-bl" />
      <div className="corner corner-br" />

      <div
        className="paper-bg"
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          zIndex: 1,
          padding: '80px 24px 60px',
        }}
      >
        <div
          className={`main-content ${showContent ? 'visible' : ''}`}
          style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '640px' }}
        >
          <Image
            src="/images/Logo.png"
            alt="北商傳書"
            width={400}
            height={260}
            style={{
              width: 'auto',
              height: 'clamp(140px, 18vw, 220px)',
              objectFit: 'contain',
              mixBlendMode: 'multiply',
              filter: 'contrast(1.08) brightness(0.97)',
              display: 'block',
              marginBottom: '10px',
            }}
            priority
          />
          <p style={{ fontFamily: "'Noto Serif TC', serif", fontSize: '13px', color: 'var(--muted)', letterSpacing: '0.38em', margin: '0 0 24px', textAlign: 'center' }}>
            書香相傳 · 惜物共好
          </p>

          <div className="ink-divider" style={{ marginBottom: '30px' }} />

          <form onSubmit={handleSearch} style={{ width: '100%' }}>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
              <input className="ink-input" type="text" placeholder="搜尋書名、作者、ISBN…" value={query} onChange={e => setQuery(e.target.value)} />
              <button type="submit" className="search-btn">搜尋</button>
            </div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '22px' }}>
              <select className="ink-select" value={category} onChange={e => setCategory(e.target.value)}>
                <option value="">全部分類</option>
                <option value="textbook">教科書</option>
                <option value="commerce">商學財金</option>
                <option value="management">管理行銷</option>
                <option value="language">語言學習</option>
                <option value="computer">資訊電腦</option>
                <option value="general">一般讀物</option>
              </select>
              <select className="ink-select" value={condition} onChange={e => setCondition(e.target.value)}>
                <option value="">書況不限</option>
                <option value="new">全新未拆</option>
                <option value="like-new">近全新</option>
                <option value="good">良好</option>
                <option value="fair">普通</option>
              </select>
            </div>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '24px', flexWrap: 'wrap' }}>
            <a href="/listings" className="post-btn">瀏覽所有書籍</a>
            <Link
              href="/listings/create"
              className="post-btn"
              style={{
                background: 'var(--seal-red)',
                color: 'var(--paper)',
                border: 'none',
                transition: 'all 0.25s ease',
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLElement).style.background = 'var(--ink)';
                (e.target as HTMLElement).style.transform = 'translateY(-2px)';
                (e.target as HTMLElement).style.boxShadow = '0 4px 12px rgba(30, 20, 10, 0.25)';
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLElement).style.background = 'var(--seal-red)';
                (e.target as HTMLElement).style.transform = 'translateY(0)';
                (e.target as HTMLElement).style.boxShadow = 'none';
              }}
            >
              刊登書籍
            </Link>
          </div>
        </div>
      </div>

      {/* 最新上架區塊 */}
      {showContent && (
        <section style={{ backgroundColor: 'var(--color-bg-primary)', padding: '0' }}>
          <div className="container-lg">
            <RecommendedListingsSection />
          </div>
        </section>
      )}

      {/* 最新上架區塊 */}
      {showContent && (
        <section style={{ backgroundColor: 'var(--color-bg-primary)', padding: '4rem 0' }}>
          <div className="container-lg">
            <LatestListingsSection />
          </div>
        </section>
      )}
    </div>
  );
}