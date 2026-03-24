'use client';

import { signIn, useSession } from 'next-auth/react';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

const ALLOWED_DOMAIN = 'ntub.edu.tw';

function ErrorAlert() {
  const params = useSearchParams();
  const error = params.get('error');

  if (!error) return null;

  const messages: Record<string, string> = {
    AccessDenied: `僅限 ${ALLOWED_DOMAIN} 校內信箱帳號，請使用學校帳號登入。`,
    OAuthSignin: '無法啟動 Google 登入，請稍後再試。',
    OAuthCallback: 'Google 登入回傳異常，請稍後再試。',
    OAuthCreateAccount: '無法建立帳號，請聯繫管理員。',
    Callback: '登入驗證過程發生錯誤，請稍後再試。',
    ServerConfigError: '伺服器設定錯誤，請聯繫管理員。',
    BackendUnreachable: '後端伺服器連線失敗，請稍後再試。',
    BackendError: '後端處理錯誤，請稍後再試。',
    BootstrapFailed: '帳號初始化失敗，請使用學校 Google 帳號。',
    Default: '登入過程發生錯誤，請稍後再試。',
  };

  const message = messages[error] ?? messages.Default;

  return (
    <div className="alert alert-danger d-flex align-items-center" role="alert">
      <i className="fas fa-exclamation-circle me-2"></i>
      <div>{message}</div>
    </div>
  );
}

function LoginContent() {
  const { data: session } = useSession();

  if (session) {
    return (
      <div className="text-center">
        <div className="spinner-border text-primary mb-3" role="status">
          <span className="visually-hidden">載入中...</span>
        </div>
        <p className="text-muted">已登入，即將跳轉...</p>
      </div>
    );
  }

  return (
    <>
      <ErrorAlert />
      <div className="text-center mb-4 mt-6">
        <h3 className="mb-2" style={{ color: '#1e140a' }}>
          <i className="fas fa-sign-in-alt me-2"></i>登入
        </h3>
        <p className="text-muted small">使用 Google 帳號一鍵登入</p>
      </div>

      <div className="d-grid gap-3">
        <button
          className="btn btn-lg d-flex align-items-center justify-content-center gap-2"
          onClick={() => signIn('google', { callbackUrl: '/auth/post-login' })}
          style={{ 
            fontSize: '1rem', 
            borderRadius: '8px', 
            padding: '0.75rem 1rem',
            backgroundColor: '#9b2335',
            color: '#f5edd8',
            border: 'none',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            const el = e.target as HTMLElement;
            el.style.backgroundColor = '#7a1a2b';
            el.style.transform = 'translateY(-2px)';
            el.style.boxShadow = '0 4px 12px rgba(155, 35, 53, 0.3)';
          }}
          onMouseLeave={(e) => {
            const el = e.target as HTMLElement;
            el.style.backgroundColor = '#9b2335';
            el.style.transform = 'translateY(0)';
            el.style.boxShadow = 'none';
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#f5edd8"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#f5edd8"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#f5edd8"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#f5edd8"
            />
          </svg>
          使用 Google 帳號登入
        </button>
      </div>

      <p className="text-center mt-4 text-muted small">
        <i className="fas fa-info-circle me-1"></i>
        僅限 <strong>{ALLOWED_DOMAIN}</strong> 校內信箱，請勿使用個人 Gmail 登入。
      </p>
    </>
  );
}

export default function LoginPage() {
  return (
    <div style={{ marginBottom: '3rem' }}>
      <div className="row justify-content-center">
        <div className="col-md-5 col-lg-4">
          <div
            className="p-4"
            style={{
              backgroundColor: '#fff',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(26, 54, 93, 0.08)',
              border: '1px solid #e8ecf0',
            }}
          >
            <Suspense fallback={
              <div className="text-center">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">載入中...</span>
                </div>
              </div>
            }>
              <LoginContent />
            </Suspense>
          </div>
        </div>
      </div>
    </div>
  );
}
