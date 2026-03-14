from django.db import models
from accounts.models import CustomUser

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    type_code = models.CharField('通知類型', max_length=50) # 如：REQUEST_ACCEPTED, NEW_MESSAGE
    title = models.CharField('標題', max_length=100)
    message = models.TextField('內容')
    related_listing_id = models.IntegerField('關聯刊登ID', null=True, blank=True)
    related_request_id = models.IntegerField('關聯請求ID', null=True, blank=True)
    is_read = models.BooleanField('已讀狀態', default=False)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)

    class Meta:
        verbose_name = '通知紀錄'
        verbose_name_plural = '通知紀錄'