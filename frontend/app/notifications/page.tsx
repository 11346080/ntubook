'use client';

import { useState, useEffect } from 'react';

interface Notification {
  id: number;
  title: string;
  message: string;
  type_code: string;
  is_read: boolean;
  created_at: string;
}

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: 1,
    title: '預約請求已接受',
    message: '你的《管理學原理》預約請求已被接受',
    type_code: 'REQUEST_ACCEPTED',
    is_read: false,
    created_at: '2026-03-21T10:30:00Z',
  },
  {
    id: 2,
    title: '新刊登提醒',
    message: '你關注的系所有新刊登：《經濟學原理》',
    type_code: 'NEW_LISTING',
    is_read: false,
    created_at: '2026-03-20T15:45:00Z',
  },
  {
    id: 3,
    title: '帳號安全提醒',
    message: '你的帳號最近進行了登入行為',
    type_code: 'ACCOUNT_SECURITY',
    is_read: true,
    created_at: '2026-03-19T09:20:00Z',
  },
];

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);

  useEffect(() => {
    // TODO: 從後端 API 取得通知列表
    // 當連接真實 API 時，反註解以下代碼：
    /*
    const fetchNotifications = async () => {
      try {
        const baseUrl = window.__BASEURL__ || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/notifications/list/`);
        const data = await response.json();
        setNotifications(data);
      } catch (err) {
        console.error('Failed to fetch notifications:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchNotifications();
    */
  }, []);

  const markAsRead = (id: number) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, is_read: true } : notif
      )
    );
  };

  const deleteNotification = (id: number) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const getNotificationIcon = (typeCode: string) => {
    switch (typeCode) {
      case 'REQUEST_ACCEPTED':
        return 'fas fa-check-circle';
      case 'NEW_LISTING':
        return 'fas fa-book';
      case 'ACCOUNT_SECURITY':
        return 'fas fa-shield-alt';
      default:
        return 'fas fa-bell';
    }
  };

  return (
    <div style={{ padding: '4rem 1rem 2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ color: '#1A365D', marginBottom: '1.5rem' }}>
        <i className="fas fa-bell"></i> 通知
      </h2>

      {notifications.length === 0 ? (
        <div className="form-section">
          <p className="text-center text-muted">暫無通知</p>
        </div>
      ) : (
        <div className="form-section">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              style={{
                padding: '1rem',
                borderLeft: `4px solid ${notif.is_read ? '#E2E8F0' : '#E67E22'}`,
                backgroundColor: notif.is_read ? '#FFFFFF' : '#FFF8F3',
                marginBottom: '1rem',
                borderRadius: '4px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                  <i className={`${getNotificationIcon(notif.type_code)}`} style={{ color: '#E67E22' }}></i>
                  <h6 style={{ margin: 0, fontWeight: 600, color: '#1E293B' }}>
                    {notif.title}
                  </h6>
                  {!notif.is_read && (
                    <span style={{
                      backgroundColor: '#E67E22',
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                    }}>
                      新
                    </span>
                  )}
                </div>
                <p style={{ margin: '0.5rem 0', color: '#475569', fontSize: '0.95rem' }}>
                  {notif.message}
                </p>
                <p style={{ margin: 0, color: '#999', fontSize: '0.85rem' }}>
                  {new Date(notif.created_at).toLocaleDateString('zh-TW')}
                </p>
              </div>
              <div style={{ marginLeft: '1rem', display: 'flex', gap: '0.5rem' }}>
                {!notif.is_read && (
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => markAsRead(notif.id)}
                    title="標記為已讀"
                  >
                    <i className="fas fa-check"></i>
                  </button>
                )}
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => deleteNotification(notif.id)}
                  title="刪除通知"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
