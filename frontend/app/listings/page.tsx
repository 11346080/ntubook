'use client';

import { useState, useEffect } from 'react';
import ListingCard from '../components/ListingCard';
// 注意：請確保 FilterSection 有處理 children 或是你直接寫 JSX
import FilterSection from '../components/FilterSection'; 

interface Listing {
  id: number;
  book: {
    title: string;
    author: string;
  };
  used_price: number;
  condition_level_display: string;
  cover_image?: string;
}

const MOCK_LISTINGS: Listing[] = [
  { 
    id: 1, 
    book: { title: '管理學原理', author: '江承曉' }, 
    used_price: 200, 
    condition_level_display: '良好', 
    cover_image: '' 
  },
  { 
    id: 2, 
    book: { title: '經濟學原理', author: '陳家聲' }, 
    used_price: 250, 
    condition_level_display: '全新', 
    cover_image: '' 
  },
  { 
    id: 3, 
    book: { title: '市場學', author: '賴文芳' }, 
    used_price: 150, 
    condition_level_display: '普通', 
    cover_image: '' 
  },
];

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>(MOCK_LISTINGS);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    keyword: '',
    isbn: '',
    min_price: '',
    max_price: '',
    department_id: '',
  });

  useEffect(() => {
    // 未來連接 API 的邏輯
    const fetchListings = async () => {
      setLoading(true);
      try {
        // const response = await fetch('http://localhost:8000/api/listings/');
        // const data = await response.json();
        // setListings(data);
        
        // 目前先模擬載入延遲
        await new Promise(resolve => setTimeout(resolve, 500));
        setListings(MOCK_LISTINGS);
      } catch (err) {
        console.error('Failed:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchListings();
  }, []);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('提交篩選:', filters);
    // 這裡之後要寫 fetch(`.../api/listings/?keyword=${filters.keyword}...`)
  };

  return (
    <div className="container py-4">
      <div className="row">
        {/* 左側篩選欄 */}
        <aside className="col-lg-3 mb-4">
          <div className="card shadow-sm p-3">
            <h5 className="mb-3 fw-bold">進階篩選</h5>
            <form onSubmit={handleFilterSubmit}>
              <div className="mb-3">
                <label className="form-label small">關鍵字</label>
                <input
                  type="text"
                  className="form-control form-control-sm"
                  name="keyword"
                  placeholder="書名、作者..."
                  value={filters.keyword}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="mb-3">
                <label className="form-label small">價格區間</label>
                <div className="d-flex align-items-center gap-2">
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    name="min_price"
                    placeholder="最低"
                    value={filters.min_price}
                    onChange={handleFilterChange}
                  />
                  <span>-</span>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    name="max_price"
                    placeholder="最高"
                    value={filters.max_price}
                    onChange={handleFilterChange}
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="form-label small">系所</label>
                <select
                  className="form-select form-select-sm"
                  name="department_id"
                  value={filters.department_id}
                  onChange={handleFilterChange}
                >
                  <option value="">所有系所</option>
                  <option value="1">會計系</option>
                  <option value="6">資管系</option>
                  {/* ...其餘選項 */}
                </select>
              </div>

              <button type="submit" className="btn btn-primary btn-sm w-100">
                <i className="fas fa-search me-1"></i> 執行搜尋
              </button>
            </form>
          </div>
        </aside>

        {/* 右側列表區域 */}
        <main className="col-lg-9">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h4 className="fw-bold m-0">所有刊登書籍</h4>
            <span className="text-muted small">共 {listings.length} 本書籍</span>
          </div>

          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status"></div>
            </div>
          ) : (
            <div className="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
              {listings.map((listing) => (
                <div key={listing.id} className="col">
                  <ListingCard listing={listing} />
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}