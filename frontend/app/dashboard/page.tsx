'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import styles from '../style/dashboard.module.css';

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

interface Listing {
  id: number;
  book: {
    title: string;
    author_display: string;
    cover_image_url?: string;
  };
  used_price: number;
  status: 'DRAFT' | 'PENDING' | 'PUBLISHED' | 'RESERVED' | 'SOLD' | 'OFF_SHELF' | 'REJECTED';
  reject_reason?: string;
  created_at: string;
  listing_images?: Array<{ file_path: string }>;
}

interface Favorite {
  id: number;
  book: {
    id: number;
    title: string;
    author_display: string;
    cover_image_url?: string;
  };
  listing?: {
    id: number;
    used_price: number;
    status: string;
  } | null;
  created_at: string;
}

interface FavoriteListItem {
  id: number;
  book_id: number;
  book_title: string;
  book_author: string;
  cover_image_url?: string;
  listing_id?: number;
  used_price?: number;
  listing_status?: string;
  created_at: string;
}

interface Reservation {
  id: number;
  listing: {
    id: number;
    book: {
      title: string;
    };
    used_price: number;
    seller?: {
      profile: {
        display_name: string;
      };
    };
  };
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'CANCELLED_BY_BUYER' | 'CANCELLED_BY_SELLER' | 'EXPIRED';
  buyer_message?: string;
  created_at: string;
  role?: 'buyer' | 'seller';
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

interface ProgramType {
  id: number;
  name_zh: string;
}

export default function DashboardPage() {
  const router = useRouter();

  const [me, setMe] = useState<MeResponse | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [programTypes, setProgramTypes] = useState<ProgramType[]>([]);
  const [allClassGroups, setAllClassGroups] = useState<ClassGroup[]>([]);
  const [activeTab, setActiveTab] = useState<'profile' | 'listings' | 'favorites' | 'reservations'>('listings');
  const [filterStatus, setFilterStatus] = useState<string>('all');  // 刊登狀態篩選器

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
  
  // 刊登、收藏、預約相關狀態
  const [listings, setListings] = useState<Listing[]>([]);
  const [favorites, setFavorites] = useState<FavoriteListItem[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loadingListings, setLoadingListings] = useState(false);
  const [loadingFavorites, setLoadingFavorites] = useState(false);
  const [loadingReservations, setLoadingReservations] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [initialStatsLoaded, setInitialStatsLoaded] = useState(false);
  const loadedTabs = useRef<Set<string>>(new Set());

  // 加載用戶資料及刊登
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

        // 2. Load profile + all stats in parallel
        Promise.all([
          fetch('http://localhost:3000/api/accounts/profile/').then(r => r.json()),
          fetch('http://localhost:8000/api/listings/my-listings/', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          }).then(r => r.ok ? r.json() : { data: [], count: 0 }),
          fetch('http://localhost:8000/api/books/favorites/', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          }).then(r => r.ok ? r.json() : { data: [], count: 0 }),
          fetch('http://localhost:8000/api/requests/my-requests/', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          }).then(r => r.ok ? r.json() : { data: [], count: 0 }),
        ]).then(([p, listingsResp, favoritesResp, reservationsResp]) => {
          setProfile(p);
          setForm({
            display_name: p.display_name ?? '',
            student_no: p.student_no ?? '',
            program_type_id: String(p.program_type_id ?? ''),
            department_id: String(p.department_id ?? ''),
            class_group_id: String(p.class_group_id ?? ''),
            grade_no: String(p.grade_no ?? ''),
          });

          // Resolve listings from { success: true, data: [...] }
          const listingsRaw = Array.isArray(listingsResp) ? listingsResp
            : (listingsResp?.data || []);
          setListings(Array.isArray(listingsRaw) ? listingsRaw : []);

          // Resolve favorites — flatten nested book/listing from API response
          const rawFav = favoritesResp?.data !== undefined
            ? (Array.isArray(favoritesResp) ? favoritesResp : favoritesResp.data || [])
            : Array.isArray(favoritesResp) ? favoritesResp : [];
          const favFlat: FavoriteListItem[] = (Array.isArray(rawFav) ? rawFav : []).map((f: Favorite) => ({
            id: f.id,
            book_id: f.book?.id ?? 0,
            book_title: f.book?.title ?? '',
            book_author: f.book?.author_display ?? '',
            cover_image_url: f.book?.cover_image_url,
            listing_id: f.listing?.id,
            used_price: f.listing?.used_price,
            listing_status: f.listing?.status,
            created_at: f.created_at,
          }));
          setFavorites(favFlat);

          // Resolve reservations
          const resvData = reservationsResp?.data !== undefined
            ? (Array.isArray(reservationsResp) ? reservationsResp : reservationsResp.data || [])
            : Array.isArray(reservationsResp) ? reservationsResp
            : [];
          setReservations(Array.isArray(resvData) ? resvData : []);

          setInitialStatsLoaded(true);
          setLoading(false);
        });
      });

    // 3. Load reference data
    Promise.all([
      fetch('http://localhost:8000/api/core/program-types/').then(r => r.json()),
      fetch('http://localhost:8000/api/core/departments/').then(r => r.json()),
      fetch('http://localhost:8000/api/core/class-groups/').then(r => r.json()),
    ]).then(([pt, dept, cg]) => {
      setProgramTypes(pt);
      setDepartments(dept);
      setAllClassGroups(cg);
    });
  }, [router]);



  // 刪除刊登
  const handleDeleteListing = async (listingId: number) => {
    if (!window.confirm('確認刪除此刊登？此動作無法復原。')) return;

    setDeleteError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/listings/${listingId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setListings(listings.filter(l => l.id !== listingId));
      } else {
        setDeleteError('刪除失敗，請稍後再試');
      }
    } catch {
      // Delete operation failed
      setDeleteError('網路錯誤，請檢查連線');
    }
  };

  // 取消收藏
  const handleRemoveFavorite = async (favoriteId: number, bookId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/books/${bookId}/favorite/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setFavorites(favorites.filter(f => f.id !== favoriteId));
      }
    } catch {
      // Remove favorite operation failed
    }
  };

  // 取消預約
  const handleCancelReservation = async (reservationId: number) => {
    if (!window.confirm('確定要取消這筆預約嗎？')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/requests/${reservationId}/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        setReservations(reservations.filter(r => r.id !== reservationId));
      } else {
        const errorData = await response.json();
        setDeleteError(errorData?.error?.message || '取消預約失敗，請稍後再試');
      }
    } catch {
      setDeleteError('網路錯誤，請檢查連線');
    }
  };

  // 當頁簽切換時加載相應數據（不在初始 mount 時執行，初始數據由第一個 useEffect 的 Promise.all 先行載入）
  useEffect(() => {
    if (!initialStatsLoaded) return;

    const loadTabData = async () => {
      if (activeTab === 'listings' && !loadedTabs.current.has('listings')) {
        loadedTabs.current.add('listings');
        setLoadingListings(true);
        try {
          const response = await fetch('http://localhost:8000/api/listings/my-listings/', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });
          if (response.ok) {
            const data = await response.json();
            setListings(Array.isArray(data) ? data : data.results || data.data || data.listings || []);
          } else if (response.status === 401) {
            router.push('/login');
          }
        } catch {
          // 載入失敗
        }
        setLoadingListings(false);
      } else if (activeTab === 'favorites' && !loadedTabs.current.has('favorites')) {
        loadedTabs.current.add('favorites');
        setLoadingFavorites(true);
        try {
          const response = await fetch('http://localhost:8000/api/books/favorites/', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });
          if (response.ok) {
            const data = await response.json();
            // Flatten favorites: { data: [{ book: {...}, listing: {...}, ... }] }
            const rawFav = data?.data !== undefined ? (Array.isArray(data) ? data : data.data || []) : Array.isArray(data) ? data : [];
            const favFlat: FavoriteListItem[] = (Array.isArray(rawFav) ? rawFav : []).map((f: Favorite) => ({
              id: f.id,
              book_id: f.book?.id ?? 0,
              book_title: f.book?.title ?? '',
              book_author: f.book?.author_display ?? '',
              cover_image_url: f.book?.cover_image_url,
              listing_id: f.listing?.id,
              used_price: f.listing?.used_price,
              listing_status: f.listing?.status,
              created_at: f.created_at,
            }));
            setFavorites(favFlat);
          }
        } catch {
          // 載入失敗
        }
        setLoadingFavorites(false);
      } else if (activeTab === 'reservations' && !loadedTabs.current.has('reservations')) {
        loadedTabs.current.add('reservations');
        setLoadingReservations(true);
        try {
          const url = 'http://localhost:8000/api/requests/my-requests/';
          
          const response = await fetch(url, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });
          
          if (response.ok) {
            const rawData = await response.json();
            
            // API 返回格式: { success: true, data: [...], count: ... }
            let reservationData: Reservation[] = [];
            if (Array.isArray(rawData)) {
              reservationData = rawData;
            } else if (rawData.data && Array.isArray(rawData.data)) {
              reservationData = rawData.data;
            } else if (rawData.results && Array.isArray(rawData.results)) {
              reservationData = rawData.results;
            }
            
            setReservations(reservationData);
          } else {
            // API 返回錯誤狀態碼
            if (response.status === 401) {
              router.push('/login');
            }
          }
        } catch {
          // 載入失敗
        }
        setLoadingReservations(false);
      }
    };

    loadTabData();
  }, [activeTab, initialStatsLoaded, router]);

  // 根據系別ID篩選班級
  const filteredClassGroups = form.department_id
    ? allClassGroups.filter(c => String(c.department) === form.department_id)
    : allClassGroups;

  // 根據學制篩選系所（當學制改變時，清空已選的系所和班級）
  const filteredDepartments = form.program_type_id
    ? departments.filter(d => String(d.program_type) === form.program_type_id)
    : departments;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(f => {
      const next = { ...f, [name]: value };
      // When program_type changes, reset department and class_group
      if (name === 'program_type_id') {
        next.department_id = '';
        next.class_group_id = '';
      }
      // When department changes, reset class_group
      if (name === 'department_id') {
        next.class_group_id = '';
      }
      return next;
    });
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

  // 獲取狀態標籤
  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { class: string; label: string }> = {
      DRAFT: { class: styles.cardBadgePending, label: '草稿' },
      PENDING: { class: styles.cardBadgePending, label: '審核中' },
      PUBLISHED: { class: styles.cardBadgePublished, label: '已上架' },
      RESERVED: { class: styles.cardBadgePublished, label: '已保留' },
      SOLD: { class: styles.cardBadgeSold, label: '已售出' },
      OFF_SHELF: { class: styles.cardBadgeSold, label: '已下架' },
      REJECTED: { class: styles.cardBadgeRejected, label: '已退回' },
    };

    const statusInfo = statusMap[status] || { class: '', label: status };
    return (
      <span className={`${styles.cardBadge} ${statusInfo.class}`}>
        {statusInfo.label}
      </span>
    );
  };

  // 獲取預約狀態標籤
  const getReservationStatusBadge = (status: string) => {
    const statusMap: Record<string, string> = {
      PENDING: styles.reservationTableStatusPending,
      ACCEPTED: styles.reservationTableStatusAccepted,
      REJECTED: styles.reservationTableStatusRejected,
      CANCELLED_BY_BUYER: styles.reservationTableStatusCancelled,
      CANCELLED_BY_SELLER: styles.reservationTableStatusCancelled,
      EXPIRED: styles.reservationTableStatusCancelled,
    };

    const statusLabelMap: Record<string, string> = {
      PENDING: '待處理',
      ACCEPTED: '已接受',
      REJECTED: '已拒絕',
      CANCELLED_BY_BUYER: '已取消',
      CANCELLED_BY_SELLER: '已取消',
      EXPIRED: '已過期',
    };

    return (
      <span className={`${styles.reservationTableStatus} ${statusMap[status] || ''}`}>
        {statusLabelMap[status] || status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>載入中...</p>
      </div>
    );
  }

  const selectedDept = departments.find(d => String(d.id) === form.department_id);
  const selectedClass = filteredClassGroups.find(c => String(c.id) === form.class_group_id);

  return (
    <div className={styles.container}>
      {/* 個人檔案卡片 */}
      <div className={styles.profileCard}>
        <div className={styles.profileContent}>
          <div className={styles.profileAvatar}>
            <i className="fas fa-user"></i>
          </div>
          <div className={styles.profileInfo}>
            <h2>{profile?.display_name ?? me?.email ?? '會員'}</h2>
            <p>
              <i className="fas fa-envelope"></i>
              {me?.email ?? ''}
            </p>
            {profile?.student_no && (
              <p>
                <i className="fas fa-id-card"></i>
                學號：{profile.student_no}
              </p>
            )}
            {selectedDept && (
              <p>
                <i className="fas fa-building"></i>
                {selectedDept.name_zh}
                {profile?.grade_no ? ` ${profile.grade_no}年級` : ''}
                {selectedClass && ` ${selectedClass.name_zh}`}
              </p>
            )}
            <div className={styles.profileStats}>
              <div className={styles.profileStat}>
                <div className={styles.profileStatValue}>{listings.length}</div>
                <div className={styles.profileStatLabel}>已刊登</div>
              </div>
              <div className={styles.profileStat}>
                <div className={styles.profileStatValue}>{favorites.length}</div>
                <div className={styles.profileStatLabel}>收藏數</div>
              </div>
              <div className={styles.profileStat}>
                <div className={styles.profileStatValue}>{reservations.length}</div>
                <div className={styles.profileStatLabel}>預約數</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 分頁籤 */}
      <div className={styles.tabsContainer}>
        {(['listings', 'favorites', 'reservations', 'profile'] as const).map(tab => (
          <button
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'listings' && <><i className="fas fa-book"></i> 我刊登的藏書</>}
            {tab === 'favorites' && <><i className="fas fa-heart"></i> 我的收藏</>}
            {tab === 'reservations' && <><i className="fas fa-envelope"></i> 我的預約</>}
            {tab === 'profile' && <><i className="fas fa-user-edit"></i> 個人資料</>}
          </button>
        ))}
      </div>

      {/* 內容區域 */}
      {activeTab === 'profile' && (
        <div className={styles.contentSection}>
          <h5>
            <i className="fas fa-edit"></i> 編輯個人資料
          </h5>

          {errors._form && <div className={`${styles.alert} ${styles.alertError}`}>{errors._form}</div>}
          {saveStatus === 'saved' && (
            <div className={`${styles.alert} ${styles.alertSuccess}`}>
              <i className="fas fa-check"></i> 儲存成功
            </div>
          )}

          <form onSubmit={handleSaveProfile}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#1e140a', fontWeight: '600' }}>
                  暱稱 *
                </label>
                <input
                  type="text"
                  name="display_name"
                  value={form.display_name}
                  onChange={handleChange}
                  maxLength={50}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: `1px solid ${errors.display_name ? '#9b2335' : '#e0d8c8'}`,
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                  }}
                />
                {errors.display_name && <small style={{ color: '#9b2335' }}>{errors.display_name}</small>}
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#1e140a', fontWeight: '600' }}>
                  學制
                </label>
                <select
                  name="program_type_id"
                  value={form.program_type_id}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #e0d8c8',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                    backgroundColor: '#fff',
                  }}
                >
                  <option value="">請選擇學制</option>
                  {programTypes.map(pt => (
                    <option key={pt.id} value={pt.id}>{pt.name_zh}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#1e140a', fontWeight: '600' }}>
                  系所
                </label>
                <select
                  name="department_id"
                  value={form.department_id}
                  onChange={handleChange}
                  disabled={!form.program_type_id}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #e0d8c8',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                    backgroundColor: form.program_type_id ? '#fff' : '#f5edd8',
                    color: form.program_type_id ? '#1e140a' : '#999',
                  }}
                >
                  <option value="">請選擇系所</option>
                  {filteredDepartments.map(d => (
                    <option key={d.id} value={d.id}>{d.name_zh}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#1e140a', fontWeight: '600' }}>
                  班級
                </label>
                <select
                  name="class_group_id"
                  value={form.class_group_id}
                  onChange={handleChange}
                  disabled={!form.department_id}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #e0d8c8',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                    backgroundColor: form.department_id ? '#fff' : '#f5edd8',
                    color: form.department_id ? '#1e140a' : '#999',
                  }}
                >
                  <option value="">請選擇班級</option>
                  {filteredClassGroups.map(cg => (
                    <option key={cg.id} value={cg.id}>{cg.name_zh}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#1e140a', fontWeight: '600' }}>
                  年級
                </label>
                <select
                  name="grade_no"
                  value={form.grade_no}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #e0d8c8',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                    backgroundColor: '#fff',
                  }}
                >
                  <option value="">請選擇年級</option>
                  <option value="1">一年級</option>
                  <option value="2">二年級</option>
                  <option value="3">三年級</option>
                  <option value="4">四年級</option>
                  <option value="5">五年級</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={saveStatus === 'saving'}
              className={styles.btnPrimary}
              style={{ minWidth: '120px' }}
            >
              {saveStatus === 'saving' ? (
                <>
                  <div className={styles.spinner} style={{ width: '16px', height: '16px' }}></div>
                  儲存中...
                </>
              ) : (
                <>
                  <i className="fas fa-save"></i> 保存
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'listings' && (
        <div className={styles.contentSection}>
          <h5>
            <i className="fas fa-book"></i> 我刊登的藏書
          </h5>

          {deleteError && <div className={`${styles.alert} ${styles.alertError}`}>{deleteError}</div>}

          {loadingListings ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>載入中...</p>
            </div>
          ) : listings.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>
                <i className="fas fa-book"></i>
              </div>
              <div className={styles.emptyStateText}>墨跡未乾，此處尚無紀錄...</div>
              <div className={styles.emptyStateSubText}>點擊右上方「發佈新書」開始刊登您的藏書</div>
            </div>
          ) : (
            <>
              {/* 狀態篩選器 */}
              <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {[
                  { value: 'all', label: '全部' },
                  { value: 'AVAILABLE', label: '刊登中' },
                  { value: 'PENDING', label: '審核中' },
                  { value: 'REJECTED', label: '已退回' },
                ].map(status => (
                  <button
                    key={status.value}
                    onClick={() => setFilterStatus(status.value)}
                    style={{
                      padding: '0.5rem 1rem',
                      border: `2px solid ${filterStatus === status.value ? '#9b2335' : '#e0d8c8'}`,
                      backgroundColor: filterStatus === status.value ? '#9b2335' : 'transparent',
                      color: filterStatus === status.value ? '#fff' : '#1e140a',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: filterStatus === status.value ? 'bold' : 'normal',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {status.label}
                  </button>
                ))}
              </div>

              {/* 刊登卡片 */}
              <div className={styles.cardGrid}>
                {listings
                  .filter(listing => filterStatus === 'all' || listing.status === filterStatus)
                  .map(listing => (
                    <div key={listing.id} className={styles.card}>
                      <div className={styles.cardImage}>
                        {listing.listing_images && listing.listing_images.length > 0 ? (
                          <img
                            src={`http://localhost:8000${listing.listing_images[0].file_path}`}
                            alt={listing.book.title}
                            onError={e => {
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className={styles.cardImagePlaceholder}>
                            <i className="fas fa-book"></i>
                          </div>
                        )}
                        {getStatusBadge(listing.status)}
                      </div>
                      <div className={styles.cardContent}>
                        <h6 className={styles.cardTitle}>{listing.book.title}</h6>
                        <p className={styles.cardAuthor}>{listing.book.author_display}</p>

                        <div className={styles.cardPrice}>NT$ {listing.used_price.toLocaleString()}</div>

                        {listing.status === 'REJECTED' && listing.reject_reason && (
                          <div className={styles.cardRejectionReason}>
                            <strong>退回原因：</strong> {listing.reject_reason}
                          </div>
                        )}

                        <div style={{ fontSize: '0.85rem', color: '#999', marginTop: 'auto', paddingTop: '1rem' }}>
                          {new Date(listing.created_at).toLocaleDateString('zh-TW')}
                        </div>

                        {listing.status === 'REJECTED' && (
                          <div className={styles.cardActions}>
                            <button
                              onClick={() => handleDeleteListing(listing.id)}
                              className={`${styles.btnDelete} ${styles.btnSmall}`}
                            >
                              <i className="fas fa-trash"></i> 刪除
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'favorites' && (
        <div className={styles.contentSection}>
          <h5>
            <i className="fas fa-heart"></i> 我的收藏
          </h5>

          {loadingFavorites ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>載入中...</p>
            </div>
          ) : favorites.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>
                <i className="fas fa-heart"></i>
              </div>
              <div className={styles.emptyStateText}>心中無二，此處尚無收藏...</div>
              <div className={styles.emptyStateSubText}>瀏覽喜愛的書籍，點擊心形按鈕即可收藏</div>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className={styles.reservationTable}>
                <thead>
                  <tr>
                    <th>書籍名稱</th>
                    <th>價格</th>
                    <th>刊登狀態</th>
                    <th>收藏時間</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {favorites.map(favorite => (
                    <tr 
                      key={favorite.id} 
                      style={{ cursor: favorite.listing_id ? 'pointer' : 'default' }} 
                      onClick={() => {
                        if (favorite.listing_id) {
                          router.push(`/listings/${favorite.listing_id}`);
                        }
                      }}
                      onMouseEnter={(e) => {
                        if (favorite.listing_id) {
                          (e.currentTarget.style.backgroundColor = '#f9f9f9');
                        }
                      }} 
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td>
                        <strong style={{ color: '#9b2335' }}>{favorite.book_title}</strong>
                        {favorite.book_author && (
                          <div style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '2px' }}>
                            {favorite.book_author}
                          </div>
                        )}
                      </td>
                      <td>
                        {favorite.used_price !== undefined
                          ? `NT$ ${favorite.used_price.toLocaleString()}`
                          : '—'}
                      </td>
                      <td>
                        {favorite.listing_status
                          ? getStatusBadge(favorite.listing_status)
                          : <span style={{ color: '#999', fontSize: '0.85rem' }}>無刊登</span>}
                      </td>
                      <td style={{ color: '#6c757d', fontSize: '0.85rem' }}>
                        {new Date(favorite.created_at).toLocaleDateString('zh-TW')}
                      </td>
                      <td>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleRemoveFavorite(favorite.id, favorite.book_id);
                          }}
                          className={`${styles.btnOutline} ${styles.btnSmall}`}
                        >
                          <i className="fas fa-trash"></i> 移除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'reservations' && (
        <div className={styles.contentSection}>
          <h5>
            <i className="fas fa-envelope"></i> 我的預約
          </h5>

          {loadingReservations ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>載入中...</p>
            </div>
          ) : reservations.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>
                <i className="fas fa-envelope"></i>
              </div>
              <div className={styles.emptyStateText}>靜待佳音，此處尚無預約...</div>
              <div className={styles.emptyStateSubText}>瀏覽書籍列表，預約您感興趣的書籍</div>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className={styles.reservationTable}>
                <thead>
                  <tr>
                    <th>書籍名稱</th>
                    <th>價格</th>
                    <th>狀態</th>
                    <th>預約時間</th>
                    {reservations.some(r => r.role) && <th>備註</th>}
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {reservations.map(reservation => (
                    <tr key={reservation.id} onClick={() => router.push(`/listings/${reservation.listing.id}`)} style={{ cursor: 'pointer' }} onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f9f9f9')} onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                      <td>
                        <strong style={{ color: '#9b2335' }}>{reservation.listing.book.title}</strong>
                      </td>
                      <td>NT$ {reservation.listing.used_price.toLocaleString()}</td>
                      <td>{getReservationStatusBadge(reservation.status)}</td>
                      <td>{new Date(reservation.created_at).toLocaleDateString('zh-TW')}</td>
                      {reservations.some(r => r.role) && <td>{reservation.buyer_message || '—'}</td>}
                      <td>
                        {reservation.status === 'PENDING' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCancelReservation(reservation.id);
                            }}
                            style={{
                              padding: '0.4rem 0.8rem',
                              border: '2px solid #9b2335',
                              backgroundColor: 'transparent',
                              color: '#9b2335',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              fontSize: '0.85rem',
                              fontWeight: 'bold',
                              transition: 'all 0.3s ease',
                            }}
                            onMouseEnter={(e) => {
                              (e.target as HTMLButtonElement).style.backgroundColor = '#9b2335';
                              (e.target as HTMLButtonElement).style.color = '#fff';
                            }}
                            onMouseLeave={(e) => {
                              (e.target as HTMLButtonElement).style.backgroundColor = 'transparent';
                              (e.target as HTMLButtonElement).style.color = '#9b2335';
                            }}
                          >
                            <i className="fas fa-times"></i> 取消
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
