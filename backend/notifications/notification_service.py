"""
通知寄送服務 / Notification Dispatcher Service

本模組職責：區分「站內通知」與「未來 email 通知」的邏輯邊界，
為未來擴充 email 功能預留乾淨的擴充點。

目前只實作站內通知建立。未來可在不修改本模組介面的情況下，
額外新增 EmailNotificationSender 或類似擴充。
"""

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationService:
    """
    通知服務

    所有通知建立統一透過此服務，不得繞過。
    目前只建立站內通知，未來可在此擴充 email 寄送邏輯。
    """

    # 預設寄件者（未來 email 通知使用）
    # 可在 settings.py 的 DEFAULT_FROM_EMAIL 或 NOTIFICATION_FROM_EMAIL 設定
    DEFAULT_FROM_EMAIL = getattr(settings, 'NOTIFICATION_FROM_EMAIL', None) or getattr(
        settings, 'DEFAULT_FROM_EMAIL', 'noreply@ntubook.com'
    )

    @classmethod
    def create(
        cls,
        user: User,
        type_code: str,
        title: str,
        message: str,
        related_listing=None,
        related_request=None,
        send_email: bool = False,
    ) -> Notification:
        """
        建立站內通知（可選同步寄送 email）。

        Params:
            user: 通知目標使用者
            type_code: 通知類型代碼，如 'REQUEST_ACCEPTED'、'LISTING_APPROVED'
            title: 通知標題
            message: 通知內文
            related_listing: 關聯刊登（可選）
            related_request: 關聯預約請求（可選）
            send_email: 是否同步寄送 email（目前無作用，預留擴充點）

        Returns:
            Notification 實例
        """
        notification = Notification.objects.create(
            user=user,
            type_code=type_code,
            title=title,
            message=message,
            related_listing=related_listing,
            related_request=related_request,
        )

        # ── 未來 email 擴充點 ──────────────────────────────────
        # 未來實作方式建議：
        #   1. 在此類中新增 send_email_to_user() 方法
        #   2. 使用 django.core.mail.send_mail 或 Celery task
        #   3. 透過 NOTIFICATION_FROM_EMAIL 設定寄件者
        #   4. 依 type_code 決定是否寄送（例如某些類型不寄 email）
        #
        # 示例框架：
        #   if send_email and user.email:
        #       cls._send_email(user, title, message)
        # ─────────────────────────────────────────────────────

        return notification

    # ── 預留：未來 email 寄送私有方法 ──────────────────────
    # @classmethod
    # def _send_email(cls, user: User, title: str, message: str) -> None:
    #     """內部：寄送 email 通知（待實作）"""
    #     send_mail(
    #         subject=title,
    #         message=message,
    #         from_email=cls.DEFAULT_FROM_EMAIL,
    #         recipient_list=[user.email],
    #         fail_silently=True,
    #     )
    # ─────────────────────────────────────────────────────


def create_notification(
    user: User,
    type_code: str,
    title: str,
    message: str,
    related_listing=None,
    related_request=None,
) -> Notification:
    """
    便利函式：建立站內通知。

    等同於 NotificationService.create()，提供更簡潔的呼叫方式。
    """
    return NotificationService.create(
        user=user,
        type_code=type_code,
        title=title,
        message=message,
        related_listing=related_listing,
        related_request=related_request,
    )
