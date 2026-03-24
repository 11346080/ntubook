'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    display_name: '',
    student_no: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password_confirm) {
      setError('密碼不相符');
      return;
    }

    // TODO: 連接至註冊 API
    alert('註冊成功！請檢查您的信箱以驗證帳號');
  };

  return (
    <div style={{ marginBottom: '2rem' }}>
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="form-section">
            <h3 style={{ textAlign: 'center', color: '#1A365D', marginBottom: '1.5rem' }}>
              <i className="fas fa-user-plus"></i> 註冊帳號
            </h3>

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="student_no">學號 *</label>
                <input
                  type="text"
                  id="student_no"
                  name="student_no"
                  placeholder="B11234567"
                  value={formData.student_no}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="display_name">暱稱 *</label>
                <input
                  type="text"
                  id="display_name"
                  name="display_name"
                  placeholder="顯示名稱"
                  value={formData.display_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">校內信箱 *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="user@ntub.edu.tw"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">密碼 *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="至少 8 位字元"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength={8}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password_confirm">確認密碼 *</label>
                <input
                  type="password"
                  id="password_confirm"
                  name="password_confirm"
                  placeholder="再次輸入密碼"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  required
                  minLength={8}
                />
              </div>

              <button type="submit" className="btn btn-primary w-100">
                <i className="fas fa-user-check"></i> 建立帳號
              </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '1.5rem', color: '#475569' }}>
              已有帳號？ <Link href="/accounts/login" style={{ color: '#E67E22' }}>登入</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
