from django.db import models
from django.conf import settings

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '待處理'), ('ACCEPTED', '已接受'), ('REJECTED', '已拒絕'),
        ('CANCELLED_BY_BUYER', '買家取消'), ('CANCELLED_BY_SELLER', '賣家取消'), ('EXPIRED', '已過期')
    ]

    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='purchase_requests')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_requests')
    status = models.CharField("狀態", max_length=25, choices=STATUS_CHOICES, default='PENDING')
    buyer_message = models.TextField("買家留言", blank=True, null=True)
    risk_score = models.DecimalField("風險分數", max_digits=5, decimal_places=2, blank=True, null=True)
    
    expires_at = models.DateTimeField("過期時間", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField("回應時間", blank=True, null=True)