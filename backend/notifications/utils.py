"""
通知工具函數 / Notification Utility Functions
"""

from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def create_notification(user, type_code, title, message, related_listing=None, related_request=None, send_email=True):
    """
    建立通知並可選地發送 Email
    
    Args:
        user: 接收通知的用户
        type_code: 通知類型代碼 (e.g., 'NEW_MESSAGE', 'NEW_REQUEST', 'REQUEST_ACCEPTED')
        title: 通知標題
        message: 通知訊息內容
        related_listing: 相關刊登 (optional)
        related_request: 相關預約請求 (optional)
        send_email: 是否發送 Email (default: True)
    
    Returns:
        Notification object
    """
    notification = Notification.objects.create(
        user=user,
        type_code=type_code,
        title=title,
        message=message,
        related_listing=related_listing,
        related_request=related_request
    )
    
    if send_email and user.email:
        send_notification_email(user, title, message)
    
    return notification


def send_notification_email(user, subject, message):
    """
    發送通知 Email
    
    Args:
        user: 接收者用户對象
        subject: 郵件主題
        message: 郵件內容
    """
    try:
        send_mail(
            subject=f'[北商傳書] {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        print(f'[EMAIL] Sent to {user.email}: {subject}')
    except Exception as e:
        print(f'[EMAIL ERROR] Failed to send email to {user.email}: {str(e)}')
