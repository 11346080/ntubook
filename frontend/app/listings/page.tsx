import { Suspense } from 'react';
import ListingCard from '../components/ListingCard';
import FilterSection from '../components/FilterSection';
import SearchResultsContent from '../components/SearchResultsContent';
import FilterForm from '../components/FilterForm';

interface SearchParams {
  keyword?: string;
  sort?: string;
  program_type_id?: string;
  department_id?: string;
  grade_no?: string;
}

export default async function ListingsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const keyword = params.keyword || '';
  const sort = params.sort || '-created_at';
  const program_type_id = params.program_type_id || '';
  const department_id = params.department_id || '';
  const grade_no = params.grade_no || '';

  return (
    <div style={{ padding: '4rem 1rem 2rem 1rem' }}>
      <div className="container py-4" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div className="row">
        {/* 左側篩選欄 */}
        <aside className="col-lg-3 mb-4">
          <FilterSection>
            <FilterForm keyword={keyword} sort={sort} program_type_id={program_type_id} department_id={department_id} grade_no={grade_no} />
          </FilterSection>
        </aside>

        {/* 右側列表區域 */}
        <main className="col-lg-9">
          <div style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ fontWeight: 700, color: '#1e140a', marginBottom: '0.5rem' }}>
              {keyword ? `搜尋結果:   "${keyword}"` : '所有刊登書籍'}
            </h4>
            {keyword && (
              <p style={{ fontSize: '0.875rem', color: '#6c757d', margin: 0 }}>
                輸入 {keyword} 搜尋結果
              </p>
            )}
          </div>

          <Suspense fallback={<LoadingSpinner />}>
            <SearchResultsContent keyword={keyword} sort={sort} program_type_id={program_type_id} department_id={department_id} grade_no={grade_no} />
          </Suspense>
        </main>
      </div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div style={{ textAlign: 'center', padding: '3rem' }}>
      <div
        style={{
          display: 'inline-block',
          width: '2rem',
          height: '2rem',
          border: '3px solid rgba(155, 35, 53, 0.3)',
          borderTop: '3px solid #9b2335',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}