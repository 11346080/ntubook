'use client';

import Link from 'next/link';
import { useState, ChangeEvent, FormEvent } from 'react';

export default function LoginPage() {
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLoginData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // TODO: 連接至實際的登入 API
      // const baseUrl = window.__BASEURL__ || 'http://localhost:8000';
      // const response = await fetch(`${baseUrl}/api/accounts/login/`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(loginData),
      // });
      // if (!response.ok) {
      //   throw new Error('登入失敗');
      // }
      // const data = await response.json();
      // localStorage.setItem('token', data.token);
      // window.location.href = '/dashboard';

      // 模擬成功登入
      setTimeout(() => {
        alert('登入成功！(模擬)');
        setLoading(false);
      }, 1000);
    } catch (err) {
      // Login error
      setError('登入失敗，請檢查帳號密碼');
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // TODO: 實作 Google OAuth 登入
  };

  return (
    <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-4">
          <div className="form-section">
            <h3 style={{ textAlign: 'center', color: '#1A365D', marginBottom: '1.5rem' }}>
              <i className="fas fa-sign-in-alt"></i> 登入
            </h3>

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email">校內信箱 (Gmail)</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="user@ntub.edu.tw"
                  value={loginData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">密碼</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="輸入密碼"
                  value={loginData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary w-100"
                disabled={loading}
              >
                {loading ? '登入中...' : '登入'}
              </button>
            </form>

            <hr style={{ margin: '1.5rem 0' }} />

            {/* Google OAuth Button */}
            <button
              type="button"
              className="btn w-100"
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                color: '#1E293B',
                marginBottom: '1rem',
              }}
              onClick={handleGoogleLogin}
            >
              <i className="fab fa-google"></i> 使用 Google 帳號登入
            </button>

            <p style={{ textAlign: 'center', marginTop: '1.5rem', color: '#475569' }}>
              還沒有帳號？ <Link href="/accounts/register" style={{ color: '#E67E22' }}>註冊</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
