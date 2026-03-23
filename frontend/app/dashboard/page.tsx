'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface MeResponse {
  user_id: number;
  email: string;
  has_profile: boolean;
  account_status: string;
}

interface ProfileResponse {
  id: number;
  display_name: string;
  student_no: string | null;
  program_type_id: number | null;
  department_id: number | null;
  class_group_id: number | null;
  grade_no: number | null;
  contact_email: string | null;
  avatar_url: string | null;
}

interface Department {
  id: number;
  program_type: number;
  name_zh: string;
}

interface ClassGroup {
  id: number;
  department: number;
  name_zh: string;
  grade_no: number;
}

export default function DashboardPage() {
  const router = useRouter();

  const [me, setMe] = useState<MeResponse | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [classGroups, setClassGroups] = useState<ClassGroup[]>([]);

  const [form, setForm] = useState({
    display_name: '',
    student_no: '',
    program_type_id: '',
    department_id: '',
    class_group_id: '',
    grade_no: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Check session via /api/me
    fetch('/api/me/')
      .then(r => {
        if (r.status === 401) {
          router.push('/login');
          return null;
        }
        return r.json();
      })
      .then(data => {
        if (!data) return;
        setMe(data);

        if (!data.has_profile) {
          router.push('/first-login');
          return;
        }

        // 2. Load profile
        fetch('http://localhost:3000/api/accounts/profile/')
          .then(r => r.json())
          .then(p => {
            setProfile(p);
            setForm({
              display_name: p.display_name ?? '',
              student_no: p.student_no ?? '',
              program_type_id: String(p.program_type_id ?? ''),
              department_id: String(p.department_id ?? ''),
              class_group_id: String(p.class_group_id ?? ''),
              grade_no: String(p.grade_no ?? ''),
            });
            setLoading(false);
          });
      });

    // 3. Load reference data
    Promise.all([
      fetch('http://localhost:8000/api/core/departments/').then(r => r.json()),
      fetch('http://localhost:8000/api/core/class-groups/').then(r => r.json()),
    ]).then(([dept, cg]) => {
      setDepartments(dept);
      setClassGroups(cg);
    });
  }, [router]);

  // Filter class groups when department changes
  useEffect(() => {
    if (form.department_id) {
      setClassGroups(prev =>
        prev.filter(c => String(c.department) === form.department_id)
      );
    }
  }, [form.department_id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (errors[name]) {
      setErrors(err => { const n = { ...err }; delete n[name]; return n; });
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    if (!form.display_name.trim()) {
      setErrors({ display_name: '請填寫顯示暱稱' });
      return;
    }

    setSaveStatus('saving');

    const body: Record<string, unknown> = { display_name: form.display_name.trim() };
    if (form.student_no.trim()) body.student_no = form.student_no.trim();
    if (form.program_type_id) body.program_type_id = parseInt(form.program_type_id);
    if (form.department_id) body.department_id = parseInt(form.department_id);
    if (form.class_group_id) body.class_group_id = parseInt(form.class_group_id);
    if (form.grade_no) body.grade_no = parseInt(form.grade_no);

    try {
      const res = await fetch('/api/accounts/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrors({ _form: data.error || '儲存失敗，請稍後再試。' });
        setSaveStatus('error');
        return;
      }

      setProfile(p => p ? { ...p, ...data } : p);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch {
      setErrors({ _form: '網路錯誤，請檢查連線後再試。' });
      setSaveStatus('error');
    }
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border text-primary" role="status" />
      </div>
    );
  }

  const selectedDept = departments.find(d => String(d.id) === form.department_id);
  const filteredClassGroups = classGroups.filter(c => String(c.department) === form.department_id);

  return (
    <div style={{ padding: '4rem 1rem 2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 使用者檔案卡片 */}
      <div className="profile-card">
        <div className="profile-content">
          <div className="profile-avatar">
            <i className="fas fa-user"></i>
          </div>
          <div className="profile-info">
            <h2>{profile?.display_name ?? me?.email ?? '會員'}</h2>
            <p><i className="fas fa-id-card"></i> 學號：{profile?.student_no ?? '未填寫'}</p>
            {selectedDept && (
              <p>
                <i className="fas fa-building"></i>{' '}
                {selectedDept.name_zh}{profile?.grade_no ? ` ${profile.grade_no}年級` : ''}
              </p>
            )}
            <p><i className="fas fa-envelope"></i> {me?.email ?? ''}</p>
            <div className="profile-stats">
              <div className="profile-stat">
                <div className="profile-stat-value">—</div>
                <div className="profile-stat-label">已刊登</div>
              </div>
              <div className="profile-stat">
                <div className="profile-stat-value">—</div>
                <div className="profile-stat-label">已售出</div>
              </div>
              <div className="profile-stat">
                <div className="profile-stat-value">—</div>
                <div className="profile-stat-label">評分</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 分頁籤 */}
      <ul className="nav nav-tabs" id="dashboardTabs" role="tablist">
        <li className="nav-item" role="presentation">
          <button
            className="nav-link active"
            type="button"
          >
            <i className="fas fa-user-edit"></i> 個人資料
          </button>
        </li>
      </ul>

      {/* Tab 內容 */}
      <div className="tab-content" id="dashboardTabContent">
        <div className="form-section">
          <h5><i className="fas fa-edit"></i> 編輯個人資料</h5>

          {errors._form && (
            <div className="alert alert-danger">{errors._form}</div>
          )}

          {saveStatus === 'saved' && (
            <div className="alert alert-success">
              <i className="fas fa-check me-1"></i> 儲存成功
            </div>
          )}

          <form onSubmit={handleSaveProfile}>
            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label htmlFor="display_name">暱稱 *</label>
                  <input
                    type="text"
                    id="display_name"
                    name="display_name"
                    className={`form-control ${errors.display_name ? 'is-invalid' : ''}`}
                    value={form.display_name}
                    onChange={handleChange}
                    maxLength={50}
                    required
                  />
                  {errors.display_name && <div className="invalid-feedback">{errors.display_name}</div>}
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label htmlFor="student_no">學號</label>
                  <input
                    type="text"
                    id="student_no"
                    name="student_no"
                    className="form-control"
                    value={form.student_no}
                    onChange={handleChange}
                    disabled
                  />
                </div>
              </div>
            </div>
            <div className="row">
              <div className="col-md-6">
                <div className="form-group">
                  <label htmlFor="program_type_id">系所</label>
                  <input
                    type="text"
                    id="department"
                    className="form-control"
                    value={selectedDept?.name_zh ?? '未填寫'}
                    disabled
                  />
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-group">
                  <label htmlFor="grade_no">年級</label>
                  <input
                    type="text"
                    id="grade_no"
                    name="grade_no"
                    className="form-control"
                    value={profile?.grade_no ? `${profile.grade_no}年級` : '未填寫'}
                    disabled
                  />
                </div>
              </div>
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saveStatus === 'saving'}
            >
              {saveStatus === 'saving' ? (
                <>
                  <span className="spinner-border spinner-border-sm me-1" role="status" />
                  儲存中...
                </>
              ) : (
                <>
                  <i className="fas fa-save me-1"></i> 保存
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
