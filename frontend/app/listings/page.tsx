'use client';

import { useState, useEffect } from 'react';
import ListingCard from '../components/ListingCard';
import FilterSection from '../components/FilterSection';

interface Listing {
  id: number;
  title: string;
  author_display: string;
  used_price: number;
  condition_level: string;
  cover_image_url?: string;
}

const MOCK_LISTINGS: Listing[] = [
  { id: 1, title: '管理學原理', author_display: '江承曉', used_price: 200, condition_level: '良好', cover_image_url: '' },
  { id: 2, title: '經濟學原理', author_display: '陳家聲', used_price: 250, condition_level: '全新', cover_image_url: '' },
  { id: 3, title: '市場學', author_display: '賴文芳', used_price: 150, condition_level: '普通', cover_image_url: '' },
];

export default function ListingsPage() {
  const [listings] = useState<Listing[]>(MOCK_LISTINGS);
  const [filters, setFilters] = useState({
    keyword: '',
    isbn: '',
    min_price: '',
    max_price: '',
    department_id: '',
    condition_level: [] as string[],
  });

  useEffect(() => {
    // TODO: 從後端 API 取得刊登列表
    // 當連接真實 API 時，反註解以下代碼：
    /*
    const fetchListings = async () => {
      try {
        const baseUrl = window.__BASEURL__ || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/listings/list/`);
        const data = await response.json();
        setListings(data);
      } catch (err) {
        console.error('Failed to fetch listings:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchListings();
    */
  }, []);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('篩選條件已提交:', filters);
    // TODO: 連接至 API 進行篩選
  };

  return (
    <div className="row mt-4">
      {/* 左側篩選欄 */}
      <div className="col-lg-3">
        <FilterSection>
          <form onSubmit={handleFilterSubmit} id="filterForm">
            {/* 關鍵字搜尋 */}
            <div className="filter-group">
              <label htmlFor="keyword">關鍵字</label>
              <input
                type="text"
                id="keyword"
                name="keyword"
                placeholder="輸入書名、作者..."
                value={filters.keyword}
                onChange={handleFilterChange}
              />
            </div>

            {/* ISBN */}
            <div className="filter-group">
              <label htmlFor="isbn">ISBN</label>
              <input
                type="text"
                id="isbn"
                name="isbn"
                placeholder="例：978-xxx..."
                value={filters.isbn}
                onChange={handleFilterChange}
              />
            </div>

            {/* 價格區間 */}
            <div className="filter-group">
              <label>價格區間 (元)</label>
              <div className="price-range">
                <input
                  type="number"
                  name="min_price"
                  placeholder="最低"
                  value={filters.min_price}
                  onChange={handleFilterChange}
                  min="0"
                />
                <span className="price-range-separator">-</span>
                <input
                  type="number"
                  name="max_price"
                  placeholder="最高"
                  value={filters.max_price}
                  onChange={handleFilterChange}
                  min="0"
                />
              </div>
            </div>

            {/* 系所篩選 */}
            <div className="filter-group">
              <label htmlFor="department_id">系所</label>
              <select
                id="department_id"
                name="department_id"
                value={filters.department_id}
                onChange={handleFilterChange}
              >
                <option value="">-- 選擇系所 --</option>
                <option value="1">會計系</option>
                <option value="2">財務管理系</option>
                <option value="3">企業管理系</option>
                <option value="4">商業設計管理系</option>
                <option value="5">國際商務系</option>
                <option value="6">資訊管理系</option>
                <option value="7">應用外語系</option>
                <option value="8">經營管理系</option>
              </select>
            </div>

            {/* 提交按鈕 */}
            <button type="submit" className="btn btn-primary w-100">
              <i className="fas fa-search"></i> 搜尋
            </button>
          </form>
        </FilterSection>
      </div>

      {/* 右側列表區域 */}
      <div className="col-lg-9">
        <div className="row">
          {listings.map((listing) => (
            <div key={listing.id} className="col-md-6 col-lg-4 mb-4">
              <ListingCard listing={listing} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
