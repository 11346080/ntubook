'use client';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/api\/?$/, '');

export interface Notification {
  id: number;
  user: number;
  type_code: string;
  title: string;
  message: string;
  related_listing: number | null;
  related_request: number | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

interface NotificationsResponse {
  success: boolean;
  data: {
    notifications: Notification[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      pages: number;
    };
  };
  error?: {
    code: string;
    message: string;
  };
}

interface UnreadCountResponse {
  success: boolean;
  data: {
    unread_count: number;
  };
}

interface MarkReadResponse {
  success: boolean;
  data: Notification;
}

interface ReadAllResponse {
  success: boolean;
  data: {
    affected_count: number;
  };
}

async function fetchWithCredentials(url: string, options?: RequestInit) {
  const res = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

export async function getNotifications(limit = 10): Promise<Notification[]> {
  try {
    const data = await fetchWithCredentials(
      `${API_BASE_URL}/api/notifications/?limit=${limit}`
    ) as NotificationsResponse;

    if (data.success) {
      return data.data.notifications;
    }
    console.warn('[notificationService] getNotifications failed:', data.error);
    return [];
  } catch (err) {
    console.warn('[notificationService] getNotifications error:', err);
    return [];
  }
}

export async function getUnreadCount(): Promise<number> {
  try {
    const data = await fetchWithCredentials(
      `${API_BASE_URL}/api/notifications/unread-count/`
    ) as UnreadCountResponse;

    if (data.success) {
      return data.data.unread_count;
    }
    return 0;
  } catch (err) {
    console.warn('[notificationService] getUnreadCount error:', err);
    return 0;
  }
}

export async function markAsRead(notificationId: number): Promise<boolean> {
  try {
    const csrfToken = getCsrfToken();
    const data = await fetchWithCredentials(
      `${API_BASE_URL}/api/notifications/${notificationId}/read/`,
      {
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrfToken },
      }
    ) as MarkReadResponse;

    return data.success;
  } catch (err) {
    console.warn('[notificationService] markAsRead error:', err);
    return false;
  }
}

export async function markAllAsRead(): Promise<boolean> {
  try {
    const csrfToken = getCsrfToken();
    const data = await fetchWithCredentials(
      `${API_BASE_URL}/api/notifications/read-all/`,
      {
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrfToken },
      }
    ) as ReadAllResponse;

    return data.success;
  } catch (err) {
    console.warn('[notificationService] markAllAsRead error:', err);
    return false;
  }
}

function getCsrfToken(): string {
  if (typeof document === 'undefined') return '';
  const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
  return cookieMatch ? cookieMatch[1] : '';
}

export function getNotificationIcon(typeCode: string): string {
  switch (typeCode) {
    case 'REQUEST_ACCEPTED':
      return 'fas fa-check-circle';
    case 'REQUEST_REJECTED':
      return 'fas fa-times-circle';
    case 'NEW_LISTING':
      return 'fas fa-book';
    case 'LISTING_APPROVED':
      return 'fas fa-check';
    case 'LISTING_REJECTED':
      return 'fas fa-ban';
    case 'RESERVATION':
      return 'fas fa-bookmark';
    case 'ACCOUNT_SECURITY':
      return 'fas fa-shield-alt';
    default:
      return 'fas fa-bell';
  }
}
