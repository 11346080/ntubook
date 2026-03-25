'use client';

import { useState, useEffect, useRef } from 'react';
import {
  Notification,
  getNotifications,
  markAsRead,
  markAllAsRead,
  getNotificationIcon,
} from '../../lib/notificationService';

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onUnreadCountChange?: (newCount: number) => void;
}

export default function NotificationPanel({
  isOpen,
  onClose,
  onUnreadCountChange,
}: NotificationPanelProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const unreadCountRef = useRef(0);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen]);

  // 點擊面板外部時關閉
  useEffect(() => {
    if (!isOpen) return;
    function handleClick(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen, onClose]);

  async function loadNotifications() {
    setLoading(true);
    const data = await getNotifications(10);
    setNotifications(data);
    unreadCountRef.current = data.filter(n => !n.is_read).length;
    setLoading(false);
  }

  async function handleMarkAsRead(id: number) {
    const ok = await markAsRead(id);
    if (ok) {
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
      if (onUnreadCountChange) {
        const newCount = Math.max(0, unreadCountRef.current - 1);
        unreadCountRef.current = newCount;
        onUnreadCountChange(newCount);
      }
    }
  }

  async function handleMarkAllAsRead() {
    const ok = await markAllAsRead();
    if (ok) {
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      if (onUnreadCountChange) {
        unreadCountRef.current = 0;
        onUnreadCountChange(0);
      }
    }
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const hasUnread = unreadCount > 0;

  function formatTime(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return '今天';
    if (diffDays === 1) return '昨天';
    if (diffDays < 7) return `${diffDays} 天前`;
    return date.toLocaleDateString('zh-TW');
  }

  return (
    <div
      ref={panelRef}
      className="notification-panel"
      style={{
        position: 'absolute',
        top: 'calc(100% + 10px)',
        right: 0,
        width: '360px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)',
        zIndex: 1000,
        overflow: 'hidden',
        border: '1px solid rgba(0, 0, 0, 0.08)',
      }}
    >
      {/* 面板頂部標題列 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.85rem 1rem',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <span
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#1A365D',
          }}
        >
          通知
        </span>
        {hasUnread && (
          <button
            onClick={handleMarkAllAsRead}
            style={{
              background: 'none',
              border: 'none',
              color: '#9B2335',
              fontSize: '12px',
              cursor: 'pointer',
              padding: '2px 6px',
              borderRadius: '4px',
            }}
          >
            全部標為已讀
          </button>
        )}
      </div>

      {/* 通知列表（可滾動） */}
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {loading ? (
          <div
            style={{
              textAlign: 'center',
              padding: '2rem',
              color: '#999',
              fontSize: '14px',
            }}
          >
            載入中...
          </div>
        ) : notifications.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '2rem',
              color: '#999',
              fontSize: '14px',
            }}
          >
            暫無通知
          </div>
        ) : (
          notifications.map(notif => (
            <div
              key={notif.id}
              style={{
                padding: '0.75rem 1rem',
                borderBottom: '1px solid #f5f5f5',
                backgroundColor: notif.is_read ? '#fff' : '#FFF8F3',
                cursor: 'pointer',
                transition: 'background 0.15s',
                display: 'flex',
                gap: '0.75rem',
                alignItems: 'flex-start',
                position: 'relative',
              }}
              onClick={() => {
                if (!notif.is_read) handleMarkAsRead(notif.id);
              }}
            >
              {/* 未讀小紅點 */}
              {!notif.is_read && (
                <span
                  style={{
                    position: 'absolute',
                    top: '14px',
                    right: '12px',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: '#9B2335',
                    flexShrink: 0,
                  }}
                />
              )}

              {/* 類型 icon */}
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: notif.is_read ? '#f0f0f0' : 'rgba(155, 35, 53, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  marginTop: '2px',
                }}
              >
                <i
                  className={getNotificationIcon(notif.type_code)}
                  style={{
                    color: notif.is_read ? '#999' : '#9B2335',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* 文字內容 */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: notif.is_read ? 400 : 600,
                    color: notif.is_read ? '#888' : '#1E293B',
                    marginBottom: '2px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    paddingRight: '16px',
                  }}
                >
                  {notif.title}
                </div>
                <div
                  style={{
                    fontSize: '12px',
                    color: '#888',
                    lineHeight: 1.4,
                    overflow: 'hidden',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    marginBottom: '3px',
                  }}
                >
                  {notif.message}
                </div>
                <div style={{ fontSize: '11px', color: '#aaa' }}>
                  {formatTime(notif.created_at)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
