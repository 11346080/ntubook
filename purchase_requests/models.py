from django.db import models
from django.conf import settings
from listings.models import Listing

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '待處理'),
        ('ACCEPTED', '已接受 (保留中)'),
        ('REJECTED', '已拒絕'),
        ('CANCELLED_BY_BUYER', '買家取消'),
        ('CANCELLED_BY_SELLER', '賣家取消'),
        ('COMPLETED', '交易完成'), # 藍圖 V2 邏輯
        ('EXPIRED', '已過期'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name='刊登商品')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests', verbose_name='買家')
    status = models.CharField('請求狀態', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    buyer_message = models.TextField('買家留言', blank=True)
    risk_score = models.DecimalField('風險分數', max_digits=5, decimal_places=2, null=True, blank=True)
    expires_at = models.DateTimeField('過期時間', null=True, blank=True)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    responded_at = models.DateTimeField('回應時間', null=True, blank=True)

    class Meta:
        verbose_name = '預約請求'
        verbose_name_plural = '預約請求管理'

    def __str__(self):
        return f"{self.buyer.username} 預約 {self.listing.book.title} ({self.get_status_display()})"