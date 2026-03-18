from django.conf import settings
from django.db import models


class Report(models.Model):
    """檢舉案件 / Report"""

    class TargetType(models.TextChoices):
        LISTING = 'LISTING', '刊登'
        USER = 'USER', '使用者'

    class ReasonCode(models.TextChoices):
        SPAM = 'SPAM', '垃圾訊息'
        SCAM = 'SCAM', '詐騙'
        INFRINGEMENT = 'INFRINGEMENT', '侵權'
        NOT_TEXTBOOK = 'NOT_TEXTBOOK', '非教科書'
        INAPPROPRIATE = 'INAPPROPRIATE', '不當內容'

    class Status(models.TextChoices):
        OPEN = 'OPEN', '待處理'
        IN_REVIEW = 'IN_REVIEW', '審查中'
        RESOLVED = 'RESOLVED', '已處理'
        DISMISSED = 'DISMISSED', '已駁回'

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_filed',
        verbose_name='檢舉人'
    )
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
        verbose_name='檢舉目標類型'
    )
    target_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports',
        verbose_name='目標刊登'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports_against',
        verbose_name='目標使用者'
    )
    reason_code = models.CharField(
        max_length=50,
        choices=ReasonCode.choices,
        verbose_name='檢舉原因'
    )
    detail = models.TextField(blank=True, null=True, verbose_name='說明')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='檢舉狀態'
    )
    risk_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='風險分數'
    )
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports_handled',
        verbose_name='處理人'
    )
    handled_at = models.DateTimeField(blank=True, null=True, verbose_name='處理時間')
    resolution_note = models.TextField(blank=True, null=True, verbose_name='處理說明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'reports'
        verbose_name = '檢舉'
        verbose_name_plural = '檢舉'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_type', 'status', 'created_at'], name='reports_target_type_status_idx'),
            models.Index(fields=['target_listing', 'status'], name='reports_target_listing_idx'),
            models.Index(fields=['target_user', 'status'], name='reports_target_user_idx'),
            models.Index(fields=['reporter', 'created_at'], name='reports_reporter_idx'),
        ]

    def __str__(self):
        return f"[{self.id}] {self.reason_code} on {self.target_type} ({self.status})"


class ModerationAction(models.Model):
    """管理處置紀錄 / Moderation Action"""

    class ActionType(models.TextChoices):
        WARN_USER = 'WARN_USER', '警告'
        SUSPEND_USER = 'SUSPEND_USER', '停權'
        UNSUSPEND_USER = 'UNSUSPEND_USER', '解除停權'
        REMOVE_LISTING = 'REMOVE_LISTING', '移除刊登'
        REQUEST_EDIT = 'REQUEST_EDIT', '要求修正'

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='moderation_actions',
        verbose_name='管理員'
    )
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name='處置類型'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderation_actions_against',
        verbose_name='目標使用者'
    )
    target_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name='目標刊登'
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name='關聯檢舉'
    )
    reason = models.TextField(verbose_name='原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    class Meta:
        db_table = 'moderation_actions'
        verbose_name = '管理處置'
        verbose_name_plural = '管理處置'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'action_type', 'created_at'], name='mod_admin_action_idx'),
            models.Index(fields=['target_user', 'created_at'], name='mod_target_user_idx'),
            models.Index(fields=['target_listing', 'created_at'], name='mod_target_listing_idx'),
        ]

    def __str__(self):
        return f"[{self.id}] {self.action_type} by {self.admin.username}"
