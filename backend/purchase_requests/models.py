from django.conf import settings
from django.db import models


class PurchaseRequest(models.Model):
    """預約請求 / Purchase Request"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', '等待中'
        ACCEPTED = 'ACCEPTED', '已接受'
        REJECTED = 'REJECTED', '已拒絕'
        CANCELLED_BY_BUYER = 'CANCELLED_BY_BUYER', '買家取消'
        CANCELLED_BY_SELLER = 'CANCELLED_BY_SELLER', '賣家取消'
        EXPIRED = 'EXPIRED', '已過期'

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        verbose_name='刊登'
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        verbose_name='買家'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='請求狀態'
    )
    buyer_message = models.TextField(blank=True, null=True, verbose_name='買家留言')
    risk_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='驗證風險分數'
    )
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='逾時時間')
    responded_at = models.DateTimeField(blank=True, null=True, verbose_name='回應時間')
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name='取消時間')
    contact_released_at = models.DateTimeField(blank=True, null=True, verbose_name='聯絡資訊開放時間')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'purchase_requests'
        verbose_name = '預約請求'
        verbose_name_plural = '預約請求'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'status', 'created_at'], name='pr_listing_status_idx'),
            models.Index(fields=['buyer', 'status', 'created_at'], name='pr_buyer_status_idx'),
            models.Index(fields=['expires_at'], name='pr_expires_at_idx'),
            models.Index(fields=['status', 'created_at'], name='pr_status_created_idx'),
        ]

    def __str__(self):
        return f"[{self.id}] {self.buyer.username} -> Listing {self.listing_id} ({self.status})"
