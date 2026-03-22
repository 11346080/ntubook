'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';

/* ── Frozen mapping ────────────────────────────────────────────────── */
const FROZEN_PROGRAM_TYPE_CODES = new Set(['3', '4', '7']);

/* 8-digit student_no rules */
const DEPT_CODE_RULES: Array<{
  program_type_code: string;
  regex: RegExp;
}> = [
  {
    program_type_code: '4',
    regex: /^\d{3}(4[1-7A-C])\d{3}$/,
  },
  {
    program_type_code: '3',
    regex: /^\d{3}(3[1-7A-B])\d{3}$/,
  },
  {
    program_type_code: '7',
    regex: /^\d{3}(5[1-7])\d{3}$/,
  },
];

/* ── Types ───────────────────────────────────────────────────────────── */
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

/* ── Parse student_no (8-digit) ─────────────────────────────────────── */
function parseStudentNo(raw: string): { program_type_code: string; dept_code: string; entry_year: string } | null {
  const trimmed = raw.trim();
  for (const rule of DEPT_CODE_RULES) {
    const m = rule.regex.exec(trimmed);
    if (m) {
      return {
        program_type_code: rule.program_type_code,
        dept_code: m[1],
        entry_year: trimmed.slice(0, 3),
      };
    }
  }
  return null;
}

/* ── Frozen dept_code → departments.code mapping ─────────────────────── */
const DEPT_CODE_TO_DB_CODE: Record<string, string> = {
  // 二技 (program_type.code = '3')
  '31': '301', '32': '302', '33': '303', '34': '304',
  '35': '305', '36': '306', '37': '307', '3A': '30A', '3B': '30B',
  // 四技 (program_type.code = '4')
  '41': '401', '42': '402', '43': '403', '44': '404',
  '45': '405', '46': '406', '47': '407', '4A': '40A', '4B': '40B', '4C': '40C',
  // 五專 (program_type.code = '7')
  '51': '521', '52': '508', '53': '503', '54': '504',
  '55': '505', '56': '506', '57': '509',
};

/* ── Resolve department.id via frozen mapping ─────────────────────────── */
function resolveDepartmentId(
  departments: Department[],
  dept_code: string,
): number | null {
  const dbCode = DEPT_CODE_TO_DB_CODE[dept_code];
  if (!dbCode) return null;
  const found = departments.find(d => d.code === dbCode);
  return found ? found.id : null;
}

/* ── Derive candidate student_no from email (@ntub.edu.tw) ─────────── */
function candidateStudentNo(email: string | null): string {
  if (!email) return '';
  const local = email.split('@')[0].toLowerCase();
  if (email.endsWith('@ntub.edu.tw') && /^\d{8}$/.test(local)) {
    return local;
  }
  return '';
}

/* ── Convert display grade_no (1-5) to DB storage format (10, 20, 30…) ── */
function toDbGradeNo(displayGrade: string): number | null {
  const n = parseInt(displayGrade, 10);
  if (isNaN(n) || n < 1 || n > 5) return null;
  return n * 10;
}

/* ── Component ──────────────────────────────────────────────────────── */
export default function FirstLoginPage() {
  const router = useRouter();

  /* Reference data */
  const [allProgramTypes, setAllProgramTypes] = useState<ProgramType[]>([]);
  const [allDepartments, setAllDepartments] = useState<Department[]>([]);
  const [allClassGroups, setAllClassGroups] = useState<ClassGroup[]>([]);

  /* Dropdown options filtered by form state */
  const [filteredDepartments, setFilteredDepartments] = useState<Department[]>([]);
  const [filteredClassGroups, setFilteredClassGroups] = useState<ClassGroup[]>([]);

  /*
   * userTouched — tracks which fields the user has manually edited.
   * While a field has NOT been touched by the user, init / re-derive
   * can write it freely. Once touched, it is only changed by direct
   * user input.
   */
  const [userTouched, setUserTouched] = useState<Record<string, boolean>>({});

  /* Form */
  const [form, setForm] = useState<FormState>({
    display_name: '',
    student_no: '',
    contact_email: '',
    program_type_id: '',
    department_id: '',
    class_group_id: '',
    grade_no: '',
  });

  /* Loading / error */
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState('');

  /*
   * initDone — set to true after the initial mount effect runs.
   * While false, the program_type useEffect does NOT reset auto-derived
   * department_id / grade_no / class_group_id, protecting the init fill.
   */
  const initDone = useRef(false);

  /* ── Load reference data ────────────────────────────────────────────── */
  const loadReferenceData = useCallback(async () => {
    const [ptRes, deptRes, cgRes] = await Promise.all([
      fetch('http://localhost:8000/api/core/program-types/'),
      fetch('http://localhost:8000/api/core/departments/'),
      fetch('http://localhost:8000/api/core/class-groups/'),
    ]);
    if (!ptRes.ok || !deptRes.ok || !cgRes.ok) {
      throw new Error('Failed to load reference data');
    }
    const [pts, depts, cgs] = await Promise.all([
      ptRes.json(), deptRes.json(), cgRes.json(),
    ]);
    return {
      programTypes: pts as ProgramType[],
      departments: depts as Department[],
      classGroups: cgs as ClassGroup[],
    };
  }, []);

  /* ── Load existing profile ────────────────────────────────────────── */
  const loadProfile = useCallback(async (): Promise<Profile | null> => {
    const res = await fetch('/api/accounts/profile/', {
      method: 'GET',
      credentials: 'include',
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json() as Promise<Profile>;
  }, []);

  /* ── Load email from NextAuth session ─────────────────────────────── */
  const loadEmail = useCallback(async (): Promise<string> => {
    try {
      const res = await fetch('/api/auth/session');
      if (!res.ok) return '';
      const data = await res.json();
      return data?.user?.email ?? '';
    } catch {
      return '';
    }
  }, []);

  /* ── Auto-fill from profile + email on mount ─────────────────────── */
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const [refData, profile, email] = await Promise.all([
          loadReferenceData(),
          loadProfile(),
          loadEmail(),
        ]);

        if (cancelled) return;

        setAllProgramTypes(refData.programTypes);
        setAllDepartments(refData.departments);
        setAllClassGroups(refData.classGroups);

        /* Candidate student_no: profile > email */
        const candidateSn =
          profile?.student_no?.trim() || candidateStudentNo(email);

        let derivedProgramTypeId: number | null = null;
        let derivedDepartmentId: number | null = null;
        let derivedGradeNo: number | null = null;

        if (candidateSn) {
          const parsed = parseStudentNo(candidateSn);
          if (parsed) {
            const pt = refData.programTypes.find(
              p => p.code === parsed.program_type_code,
            );
            if (pt && FROZEN_PROGRAM_TYPE_CODES.has(pt.code)) {
              derivedProgramTypeId = pt.id;
              derivedDepartmentId = resolveDepartmentId(
                refData.departments,
                parsed.dept_code,
              );
              /* grade_no = currentAcademicYear - entry_year */
              const entryYear = parseInt(parsed.entry_year, 10);
              if (!isNaN(entryYear)) {
                derivedGradeNo = 115 - entryYear;
                if (derivedGradeNo < 1) derivedGradeNo = 1;
                if (derivedGradeNo > 5) derivedGradeNo = 5;
              }
            }
          }
        }

        /* ── Fill form: profile values take absolute priority ──────────── */
        setForm({
          display_name: profile?.display_name ?? '',
          student_no: profile?.student_no ?? candidateSn,
          contact_email: profile?.contact_email ?? email,
          program_type_id:
            profile?.program_type_id != null
              ? String(profile.program_type_id)
              : derivedProgramTypeId != null
              ? String(derivedProgramTypeId)
              : '',
          department_id:
            profile?.department_id != null
              ? String(profile.department_id)
              : derivedDepartmentId != null
              ? String(derivedDepartmentId)
              : '',
          class_group_id:
            profile?.class_group_id != null
              ? String(profile.class_group_id)
              : '',
          grade_no:
            profile?.grade_no != null
              ? String(profile.grade_no)
              : derivedGradeNo != null
              ? String(derivedGradeNo)
              : '',
        });

        initDone.current = true;

      } catch {
        if (!cancelled) {
          setFormError('無法載入資料，請重新整理頁面。');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [loadReferenceData, loadProfile, loadEmail]);

  /* ── Filter departments when program_type changes ─────────────────── */
  useEffect(() => {
    if (form.program_type_id) {
      setFilteredDepartments(
        allDepartments.filter(
          d => String(d.program_type) === form.program_type_id,
        ),
      );
    } else {
      setFilteredDepartments([]);
    }
    /*
     * initDone gate: during initial mount the auto-derived values have
     * already been written by the init effect. Do NOT overwrite them.
     * Only clear fields that the user has NOT touched.
     */
    if (!initDone.current) return;

    setForm(prev => ({
      ...prev,
      department_id: userTouched['department_id'] ? prev.department_id : '',
      class_group_id: userTouched['class_group_id'] ? prev.class_group_id : '',
      grade_no:      userTouched['grade_no']      ? prev.grade_no      : '',
    }));
    setFilteredClassGroups([]);
  }, [form.program_type_id, allDepartments, userTouched]);

  /* ── Filter class groups when department OR grade_no changes ──────── */
  useEffect(() => {
    if (form.department_id) {
      const dbGrade = toDbGradeNo(form.grade_no);
      setFilteredClassGroups(
        allClassGroups.filter(c => {
          const deptMatch = String(c.department) === form.department_id;
          const gradeMatch = dbGrade !== null ? c.grade_no === dbGrade : true;
          return deptMatch && gradeMatch;
        }),
      );
    } else {
      setFilteredClassGroups([]);
    }
  }, [form.department_id, form.grade_no, allClassGroups]);

  /* ── Handle student_no change: re-derive all derived fields ──────── */
  const handleStudentNoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    setForm(prev => ({ ...prev, student_no: raw }));

    /* Only auto-derive if the user has not manually touched those fields */
    if (!userTouched['program_type_id'] && !userTouched['department_id'] && !userTouched['grade_no']) {
      const parsed = parseStudentNo(raw);
      if (parsed) {
        const pt = allProgramTypes.find(p => p.code === parsed.program_type_code);
        if (pt && FROZEN_PROGRAM_TYPE_CODES.has(pt.code)) {
          const deptId = resolveDepartmentId(allDepartments, parsed.dept_code);
          const entryYear = parseInt(parsed.entry_year, 10);
          let grade = '';
          if (!isNaN(entryYear)) {
            const g = 115 - entryYear;
            if (g >= 1 && g <= 5) grade = String(g);
          }
          setForm(prev => ({
            ...prev,
            program_type_id: String(pt.id),
            department_id: deptId != null ? String(deptId) : prev.department_id,
            grade_no: grade || prev.grade_no,
          }));
        }
      }
    }
  };

  /* ── Generic field change ─────────────────────────────────────────── */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    setUserTouched(prev => ({ ...prev, [name]: true }));
    if (errors[name]) {
      setErrors(err => { const n = { ...err }; delete n[name]; return n; });
    }
  };

  /* ── Submit ────────────────────────────────────────────────────────── */
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
      const profileRes = await fetch('/api/accounts/profile/', {
        method: 'GET',
        credentials: 'include',
      });
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
      const res = await fetch('/api/accounts/profile/', {
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

      const meRes = await fetch('http://localhost:8000/api/accounts/me/', {
        method: 'GET',
        credentials: 'include',
      });
      if (meRes.ok) {
        const meData = await meRes.json();
        if (meData.profile_completed || meData.has_profile) {
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
      <div className="text-center mt-5">
        <div className="spinner-border text-primary" role="status" />
      </div>
    );
  }

  return (
    <div className="container mt-4" style={{ maxWidth: 640 }}>
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><a href="/">首頁</a></li>
          <li className="breadcrumb-item active">首次登入</li>
        </ol>
      </nav>

      <div
        className="p-4"
        style={{ background: '#fff', borderRadius: 12, border: '1px solid #e8ecf0', boxShadow: '0 4px 20px rgba(26,54,93,0.08)' }}
      >
        <h4 style={{ color: '#1A365D' }} className="mb-1">
          <i className="fas fa-user-edit me-2" />
          建立個人檔案
        </h4>
        <p className="text-muted small mb-4">請填寫以下資料以完成會員註冊</p>

        {formError && <div className="alert alert-danger">{formError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          {/* 基本資訊 */}
          <fieldset className="mb-4">
            <legend className="h6 text-primary border-bottom pb-1 mb-3">基本資訊</legend>

            <div className="mb-3">
              <label className="form-label" htmlFor="display_name">
                顯示暱稱 <span className="text-danger">*</span>
              </label>
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

            <div className="mb-3">
              <label className="form-label" htmlFor="student_no">學號</label>
              <input
                type="text"
                id="student_no"
                name="student_no"
                className="form-control"
                value={form.student_no}
                onChange={handleStudentNoChange}
                placeholder="填寫後將自動帶入學制、系所與年級"
              />
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="contact_email">聯絡信箱</label>
              <input
                type="email"
                id="contact_email"
                name="contact_email"
                className="form-control"
                value={form.contact_email}
                onChange={handleChange}
                placeholder="選填"
              />
            </div>
          </fieldset>

          {/* 學籍資訊 */}
          <fieldset className="mb-4">
            <legend className="h6 text-primary border-bottom pb-1 mb-3">學籍資訊</legend>

            <div className="mb-3">
              <label className="form-label" htmlFor="program_type_id">
                學制 <span className="text-danger">*</span>
              </label>
              <select
                id="program_type_id"
                name="program_type_id"
                className={`form-select ${errors.program_type_id ? 'is-invalid' : ''}`}
                value={form.program_type_id}
                onChange={handleChange}
              >
                <option value="">請選擇學制</option>
                {allProgramTypes
                  .filter(pt => FROZEN_PROGRAM_TYPE_CODES.has(pt.code))
                  .map(pt => (
                    <option key={pt.id} value={pt.id}>{pt.name_zh}</option>
                  ))
                }
              </select>
              {errors.program_type_id && <div className="invalid-feedback">{errors.program_type_id}</div>}
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="department_id">
                系所 <span className="text-danger">*</span>
              </label>
              <select
                id="department_id"
                name="department_id"
                className={`form-select ${errors.department_id ? 'is-invalid' : ''}`}
                value={form.department_id}
                onChange={handleChange}
                disabled={!form.program_type_id}
              >
                <option value="">
                  {form.program_type_id ? '請選擇系所' : '請先選擇學制'}
                </option>
                {filteredDepartments.map(d => (
                  <option key={d.id} value={d.id}>{d.name_zh}</option>
                ))}
              </select>
              {errors.department_id && <div className="invalid-feedback">{errors.department_id}</div>}
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="grade_no">年級</label>
              <select
                id="grade_no"
                name="grade_no"
                className="form-select"
                value={form.grade_no}
                onChange={handleChange}
              >
                <option value="">請選擇</option>
                {[1, 2, 3, 4, 5].map(g => (
                  <option key={g} value={g}>{g}年級</option>
                ))}
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="class_group_id">班級</label>
              <select
                id="class_group_id"
                name="class_group_id"
                className="form-select"
                value={form.class_group_id}
                onChange={handleChange}
                disabled={!form.department_id}
              >
                <option value="">
                  {form.department_id ? '請選擇班級' : '請先選擇系所'}
                </option>
                {filteredClassGroups.map(c => (
                  <option key={c.id} value={c.id}>{c.name_zh}</option>
                ))}
              </select>
            </div>
          </fieldset>

          <div className="d-flex justify-content-between align-items-center">
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => router.push('/dashboard')}
            >
              稍後再填
            </button>
            <button
              type="submit"
              className="btn btn-primary px-4"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-1" role="status" />
                  送出中...
                </>
              ) : (
                <>
                  <i className="fas fa-check me-1" />
                  送出
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
