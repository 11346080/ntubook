from django.conf import settings
from django.db import models


class Notification(models.Model):
    """通知 / Notification"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='使用者'
    )
    type_code = models.CharField(max_length=50, verbose_name='通知類型')
    title = models.CharField(max_length=200, verbose_name='標題')
    message = models.CharField(max_length=500, verbose_name='訊息')
    related_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notifications',
        verbose_name='關聯刊登'
    )
    related_request = models.ForeignKey(
        'purchase_requests.PurchaseRequest',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notifications',
        verbose_name='關聯請求'
    )
    is_read = models.BooleanField(default=False, verbose_name='是否已讀')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='已讀時間')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at'], name='notif_user_read_created_idx'),
            models.Index(fields=['user', 'type_code', 'created_at'], name='notif_user_type_created_idx'),
        ]

    def __str__(self):
        return f"[{self.id}] {self.title} ({self.user.username})"
