from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type_code = models.CharField("通知類型", max_length=50)
    title = models.CharField("標題", max_length=100)
    message = models.TextField("訊息內容")
    related_listing_id = models.IntegerField("相關刊登ID", blank=True, null=True)
    related_request_id = models.IntegerField("相關請求ID", blank=True, null=True)
    is_read = models.BooleanField("是否已讀", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField("讀取時間", blank=True, null=True)