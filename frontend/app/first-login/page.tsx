'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface ProgramType {
  id: number;
  code: string;
  name_zh: string;
}

interface Department {
  id: number;
  code: string;
  program_type: number;
  name_zh: string;
}

interface ClassGroup {
  id: number;
  department: number;
  name_zh: string;
  grade_no: number;
}

interface Profile {
  id: number;
  display_name: string;
  student_no: string | null;
  program_type_id: number | null;
  department_id: number | null;
  class_group_id: number | null;
  grade_no: number | null;
  contact_email: string | null;
}

interface FormState {
  display_name: string;
  student_no: string;
  contact_email: string;
  program_type_id: string;
  department_id: string;
  class_group_id: string;
  grade_no: string;
}

export default function FirstLoginPage() {
  const router = useRouter();

  const [allProgramTypes, setAllProgramTypes] = useState<ProgramType[]>([]);
  const [allDepartments, setAllDepartments] = useState<Department[]>([]);
  const [allClassGroups, setAllClassGroups] = useState<ClassGroup[]>([]);

  const [filteredDepartments, setFilteredDepartments] = useState<Department[]>([]);
  const [filteredClassGroups, setFilteredClassGroups] = useState<ClassGroup[]>([]);

  const [form, setForm] = useState<FormState>({
    display_name: '',
    student_no: '',
    contact_email: '',
    program_type_id: '',
    department_id: '',
    class_group_id: '',
    grade_no: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState('');

  const loadReferenceData = useCallback(async () => {
    const [ptRes, deptRes, cgRes] = await Promise.all([
      fetch('/backend-api/core/program-types/'),
      fetch('/backend-api/core/departments/'),
      fetch('/backend-api/core/class-groups/'),
    ]);
    if (!ptRes.ok || !deptRes.ok || !cgRes.ok) throw new Error('Failed to load reference data');
    const [pts, depts, cgs] = await Promise.all([ptRes.json(), deptRes.json(), cgRes.json()]);
    return { programTypes: pts as ProgramType[], departments: depts as Department[], classGroups: cgs as ClassGroup[] };
  }, []);

  const loadProfile = useCallback(async (): Promise<Profile | null> => {
    const res = await fetch('/api/accounts/profile', { method: 'GET' });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json() as Promise<Profile>;
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [refData, profile] = await Promise.all([loadReferenceData(), loadProfile()]);
        if (cancelled) return;

        setAllProgramTypes(refData.programTypes);
        setAllDepartments(refData.departments);
        setAllClassGroups(refData.classGroups);

        // 不再自動推導：所有學籍欄位由使用者自行選擇
        setForm({
          display_name: profile?.display_name ?? '',
          student_no: profile?.student_no ?? '',
          contact_email: profile?.contact_email ?? '',
          program_type_id: profile?.program_type_id != null ? String(profile.program_type_id) : '',
          department_id: profile?.department_id != null ? String(profile.department_id) : '',
          class_group_id: profile?.class_group_id != null ? String(profile.class_group_id) : '',
          grade_no: profile?.grade_no != null ? String(profile.grade_no) : '',
        });

      } catch {
        if (!cancelled) setFormError('無法載入資料，請重新整理頁面。');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [loadReferenceData, loadProfile]);

  // 連動：選擇學制 → 過濾系所
  useEffect(() => {
    if (form.program_type_id) {
      setFilteredDepartments(allDepartments.filter(d => String(d.program_type) === form.program_type_id));
    } else {
      setFilteredDepartments([]);
    }
    // 學制改變時，清空系所、班級、年級
    setForm(prev => ({
      ...prev,
      department_id: '',
      class_group_id: '',
      grade_no: '',
    }));
    setFilteredClassGroups([]);
  }, [form.program_type_id, allDepartments]);

  // 連動：選擇系所 → 過濾班級（班級連動年級一起篩選）
  useEffect(() => {
    if (form.department_id) {
      const gradeValue = form.grade_no ? parseInt(form.grade_no, 10) : null;
      setFilteredClassGroups(
        allClassGroups.filter(c => {
          const deptMatch = String(c.department) === form.department_id;
          const gradeMatch = gradeValue !== null ? c.grade_no === gradeValue * 10 : true;
          return deptMatch && gradeMatch;
        })
      );
    } else {
      setFilteredClassGroups([]);
    }
    // 系所改變時，清空班級
    setForm(prev => ({ ...prev, class_group_id: '' }));
  }, [form.department_id, form.grade_no, allClassGroups]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    // 年級改變時，重新過濾班級
    if (name === 'grade_no') {
      if (form.department_id) {
        const gradeValue = value ? parseInt(value, 10) : null;
        setFilteredClassGroups(
          allClassGroups.filter(c => {
            const deptMatch = String(c.department) === form.department_id;
            const gradeMatch = gradeValue !== null ? c.grade_no === gradeValue * 10 : true;
            return deptMatch && gradeMatch;
          })
        );
        setForm(prev => ({ ...prev, grade_no: value, class_group_id: '' }));
        return;
      }
    }
    if (errors[name]) {
      setErrors(err => { const n = { ...err }; delete n[name]; return n; });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setFormError('');

    if (!form.display_name.trim()) {
      setErrors({ display_name: '請填寫顯示暱稱' });
      return;
    }
    if (!form.program_type_id) {
      setErrors({ program_type_id: '請選擇學制' });
      return;
    }
    if (!form.department_id) {
      setErrors({ department_id: '請選擇系所' });
      return;
    }

    setSubmitting(true);

    try {
      const profileRes = await fetch('/api/accounts/profile', { method: 'GET' });
      const profileExists = profileRes.ok && profileRes.status !== 404;

      const body: Record<string, unknown> = {
        display_name: form.display_name.trim(),
        program_type_id: parseInt(form.program_type_id),
        department_id: parseInt(form.department_id),
        contact_email: form.contact_email.trim() || null,
        student_no: form.student_no.trim() || null,
      };
      if (form.class_group_id) body.class_group_id = parseInt(form.class_group_id);
      if (form.grade_no) body.grade_no = parseInt(form.grade_no);

      const method = profileExists ? 'PATCH' : 'POST';
      const res = await fetch('/api/accounts/profile', {
        method,
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        if (data.error === 'PROFILE_EXISTS') {
          router.push('/dashboard');
          return;
        }
        setFormError(data.error || '儲存失敗，請稍後再試。');
        setSubmitting(false);
        return;
      }

      const meRes = await fetch('/api/me');
      if (meRes.ok) {
        const meData = await meRes.json();
        if (meData.has_profile) {
          router.push('/dashboard');
          return;
        }
      }
      if (data.has_profile !== false) {
        router.push('/dashboard');
        return;
      }
      setFormError('請確認所有必填欄位。');
    } catch {
      setFormError('網路錯誤，請檢查連線後再試。');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f5edd8' }}>
        <div className="spinner-border" style={{ color: '#9b2335' }} role="status" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5edd8', padding: '4rem 1rem 2rem 1rem' }}>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        <nav aria-label="breadcrumb" className="mb-4">
          <ol className="breadcrumb" style={{ backgroundColor: 'transparent', marginBottom: 0 }}>
            <li className="breadcrumb-item"><a href="/" style={{ color: '#9b2335', textDecoration: 'none' }}>首頁</a></li>
            <li className="breadcrumb-item active" style={{ color: '#6c757d' }}>首次登入</li>
          </ol>
        </nav>

        <div style={{ background: '#ffffff', borderRadius: 12, border: '2px solid #e0d8c8', boxShadow: '0 4px 20px rgba(155, 35, 53, 0.08)', padding: '2rem' }}>
          <h4 style={{ color: '#9b2335', marginBottom: '0.5rem', fontWeight: '600' }}>
            <i className="fas fa-user-edit me-2" />
            建立個人檔案
          </h4>
          <p style={{ color: '#6c757d', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            請填寫以下資料以完成會員註冊
          </p>

          {formError && (
            <div style={{ backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', color: '#721c24', padding: '0.75rem 1rem', borderRadius: 6, marginBottom: '1rem' }}>
              {formError}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <fieldset className="mb-4" style={{ border: 'none', padding: 0 }}>
              <legend style={{ fontSize: '0.95rem', fontWeight: '600', color: '#9b2335', borderBottom: '2px solid #e0d8c8', paddingBottom: '0.5rem', marginBottom: '1rem' }}>基本資訊</legend>

              <div className="mb-3">
                <label className="form-label" htmlFor="display_name" style={{ color: '#1e140a', fontWeight: '500' }}>
                  顯示暱稱 <span style={{ color: '#9b2335' }}>*</span>
                </label>
                <input
                  type="text"
                  id="display_name"
                  name="display_name"
                  className="form-control"
                  style={{ borderColor: errors.display_name ? '#9b2335' : '#e0d8c8', boxShadow: errors.display_name ? '0 0 0 0.2rem rgba(155, 35, 53, 0.25)' : 'none', color: '#1e140a' }}
                  value={form.display_name}
                  onChange={handleChange}
                  maxLength={50}
                  required
                />
                {errors.display_name && <div style={{ color: '#9b2335', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.display_name}</div>}
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="student_no" style={{ color: '#1e140a', fontWeight: '500' }}>學號</label>
                <input type="text" id="student_no" name="student_no" className="form-control" style={{ borderColor: '#e0d8c8', color: '#1e140a' }} value={form.student_no} onChange={handleChange} placeholder="選填" />
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="contact_email" style={{ color: '#1e140a', fontWeight: '500' }}>聯絡信箱</label>
                <input type="email" id="contact_email" name="contact_email" className="form-control" style={{ borderColor: '#e0d8c8', color: '#1e140a' }} value={form.contact_email} onChange={handleChange} placeholder="選填" />
              </div>
            </fieldset>

            <fieldset className="mb-4" style={{ border: 'none', padding: 0 }}>
              <legend style={{ fontSize: '0.95rem', fontWeight: '600', color: '#9b2335', borderBottom: '2px solid #e0d8c8', paddingBottom: '0.5rem', marginBottom: '1rem' }}>學籍資訊</legend>

              <div className="mb-3">
                <label className="form-label" htmlFor="program_type_id" style={{ color: '#1e140a', fontWeight: '500' }}>學制 <span style={{ color: '#9b2335' }}>*</span></label>
                <select id="program_type_id" name="program_type_id" className="form-select" style={{ borderColor: errors.program_type_id ? '#9b2335' : '#e0d8c8', boxShadow: errors.program_type_id ? '0 0 0 0.2rem rgba(155, 35, 53, 0.25)' : 'none', color: '#1e140a' }} value={form.program_type_id} onChange={handleChange}>
                  <option value="">請選擇學制</option>
                  {allProgramTypes.map(pt => (<option key={pt.id} value={pt.id}>{pt.name_zh}</option>))}
                </select>
                {errors.program_type_id && <div style={{ color: '#9b2335', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.program_type_id}</div>}
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="department_id" style={{ color: '#1e140a', fontWeight: '500' }}>系所 <span style={{ color: '#9b2335' }}>*</span></label>
                <select id="department_id" name="department_id" className="form-select" style={{ borderColor: errors.department_id ? '#9b2335' : '#e0d8c8', boxShadow: errors.department_id ? '0 0 0 0.2rem rgba(155, 35, 53, 0.25)' : 'none', color: '#1e140a', opacity: !form.program_type_id ? 0.5 : 1, cursor: !form.program_type_id ? 'not-allowed' : 'pointer' }} value={form.department_id} onChange={handleChange} disabled={!form.program_type_id}>
                  <option value="">{form.program_type_id ? '請選擇系所' : '請先選擇學制'}</option>
                  {filteredDepartments.map(d => (<option key={d.id} value={d.id}>{d.name_zh}</option>))}
                </select>
                {errors.department_id && <div style={{ color: '#9b2335', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.department_id}</div>}
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="grade_no" style={{ color: '#1e140a', fontWeight: '500' }}>年級</label>
                <select id="grade_no" name="grade_no" className="form-select" style={{ borderColor: '#e0d8c8', color: '#1e140a' }} value={form.grade_no} onChange={handleChange}>
                  <option value="">請選擇</option>
                  {[1, 2, 3, 4, 5].map(g => (<option key={g} value={g}>{g}年級</option>))}
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="class_group_id" style={{ color: '#1e140a', fontWeight: '500' }}>班級</label>
                <select id="class_group_id" name="class_group_id" className="form-select" style={{ borderColor: '#e0d8c8', color: '#1e140a', opacity: !form.department_id ? 0.5 : 1, cursor: !form.department_id ? 'not-allowed' : 'pointer' }} value={form.class_group_id} onChange={handleChange} disabled={!form.department_id}>
                  <option value="">{form.department_id ? '請選擇班級' : '請先選擇系所'}</option>
                  {filteredClassGroups.map(c => (<option key={c.id} value={c.id}>{c.name_zh}</option>))}
                </select>
              </div>
            </fieldset>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', marginTop: '2rem' }}>
              <button type="button" style={{ padding: '0.5rem 1rem', borderRadius: 6, border: '2px solid #e0d8c8', backgroundColor: '#ffffff', color: '#6c757d', cursor: 'pointer', fontWeight: '500', fontSize: '0.95rem', transition: 'all 0.2s' }} onMouseEnter={(e) => { (e.target as HTMLButtonElement).style.borderColor = '#9b2335'; (e.target as HTMLButtonElement).style.color = '#9b2335'; }} onMouseLeave={(e) => { (e.target as HTMLButtonElement).style.borderColor = '#e0d8c8'; (e.target as HTMLButtonElement).style.color = '#6c757d'; }} onClick={() => router.push('/dashboard')}>稍後再填</button>
              <button type="submit" style={{ padding: '0.5rem 1.5rem', borderRadius: 6, border: 'none', backgroundColor: '#9b2335', color: '#ffffff', cursor: submitting ? 'not-allowed' : 'pointer', fontWeight: '500', fontSize: '0.95rem', opacity: submitting ? 0.7 : 1, transition: 'all 0.2s' }} onMouseEnter={(e) => { if (!submitting) (e.target as HTMLButtonElement).style.backgroundColor = '#7a1a2b'; }} onMouseLeave={(e) => { (e.target as HTMLButtonElement).style.backgroundColor = '#9b2335'; }} disabled={submitting}>
                {submitting ? (<><span className="spinner-border spinner-border-sm me-1" role="status" style={{ borderColor: '#ffffff' }} />送出中...</>) : (<><i className="fas fa-check me-1" />送出</>)}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
