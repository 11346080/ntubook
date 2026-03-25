'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface FilterFormProps {
  keyword: string;
  sort: string;
  program_type_id?: string;
  department_id?: string;
  grade_no?: string;
}

interface ProgramType { id: number; name_zh: string; }
interface Department { id: number; name_zh: string; program_type: number; }
interface ClassGroup { id: number; name_zh: string; department: number; grade_no: number; }

export default function FilterForm({
  keyword: initialKeyword,
  sort: initialSort,
  program_type_id: initialProgramTypeId,
  department_id: initialDepartmentId,
  grade_no: initialGradeNo,
}: FilterFormProps) {
  const router = useRouter();

  const [keyword, setKeyword] = useState(initialKeyword);
  const [sort, setSort] = useState(initialSort);
  const [program_type_id, setProgramTypeId] = useState(initialProgramTypeId || '');
  const [department_id, setDepartmentId] = useState(initialDepartmentId || '');
  const [grade_no, setGradeNo] = useState(initialGradeNo || '');

  const [allProgramTypes, setAllProgramTypes] = useState<ProgramType[]>([]);
  const [allDepartments, setAllDepartments] = useState<Department[]>([]);
  const [filteredDepartments, setFilteredDepartments] = useState<Department[]>([]);

  // 載入學制、系所資料
  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    Promise.all([
      fetch(`${API_BASE}/core/program-types/`).then(r => r.json()),
      fetch(`${API_BASE}/core/departments/`).then(r => r.json()),
    ]).then(([pts, depts]) => {
      setAllProgramTypes(pts as ProgramType[]);
      setAllDepartments(depts as Department[]);
    });
  }, []);

  // 學制改變 → 過濾系所
  useEffect(() => {
    if (program_type_id) {
      setFilteredDepartments(allDepartments.filter(d => String(d.program_type) === program_type_id));
    } else {
      setFilteredDepartments([]);
    }
    // 學制改變時，清空系所、年級
    setDepartmentId('');
    setGradeNo('');
  }, [program_type_id, allDepartments]);

  // 系所改變時，清空年級
  useEffect(() => {
    setGradeNo('');
  }, [department_id]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (keyword.trim()) {
      params.append('keyword', keyword.trim());
    }
    if (program_type_id) {
      params.append('program_type_id', program_type_id);
    }
    if (department_id) {
      params.append('department_id', department_id);
    }
    if (grade_no) {
      params.append('grade_no', grade_no);
    }
    if (sort) {
      params.append('sort', sort);
    }
    params.append('page', '1');
    router.push(`/listings?${params.toString()}`);
  };

  const handleClear = () => {
    setKeyword('');
    setSort('-created_at');
    setProgramTypeId('');
    setDepartmentId('');
    setGradeNo('');
    router.push('/listings');
  };

  const hasFilters = keyword || program_type_id || department_id || grade_no || sort !== '-created_at';

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

        {/* 學制 / Program Type */}
        <div>
          <label
            htmlFor="program_type_id"
            style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '0.5rem',
              color: '#1e140a',
            }}
          >
            學制
          </label>
          <select
            id="program_type_id"
            value={program_type_id}
            onChange={(e) => setProgramTypeId(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              color: '#1e140a',
              backgroundColor: 'white',
              cursor: 'pointer',
            }}
          >
            <option value="">所有學制</option>
            {allProgramTypes.map(pt => (
              <option key={pt.id} value={pt.id}>{pt.name_zh}</option>
            ))}
          </select>
        </div>

        {/* 系所 / Department */}
        <div>
          <label
            htmlFor="department_id"
            style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '0.5rem',
              color: '#1e140a',
            }}
          >
            系所
          </label>
          <select
            id="department_id"
            value={department_id}
            onChange={(e) => setDepartmentId(e.target.value)}
            disabled={!program_type_id}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              color: program_type_id ? '#1e140a' : '#999',
              backgroundColor: program_type_id ? 'white' : '#f5f5f5',
              cursor: program_type_id ? 'pointer' : 'not-allowed',
            }}
          >
            <option value="">{program_type_id ? '所有系所' : '請先選擇學制'}</option>
            {filteredDepartments.map(d => (
              <option key={d.id} value={d.id}>{d.name_zh}</option>
            ))}
          </select>
        </div>

        {/* 年級 / Grade */}
        <div>
          <label
            htmlFor="grade_no"
            style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '0.5rem',
              color: '#1e140a',
            }}
          >
            年級
          </label>
          <select
            id="grade_no"
            value={grade_no}
            onChange={(e) => setGradeNo(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              color: '#1e140a',
              backgroundColor: 'white',
              cursor: 'pointer',
            }}
          >
            <option value="">所有年級</option>
            {[1, 2, 3, 4, 5].map(g => (
              <option key={g} value={g}>{g}年級</option>
            ))}
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
        {hasFilters && (
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
