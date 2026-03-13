from django.db import models
from django.conf import settings

class Report(models.Model):
    TARGET_CHOICES = [('listing', '刊登'), ('user', '使用者')]
    STATUS_CHOICES = [('OPEN', '未處理'), ('IN_REVIEW', '審核中'), ('RESOLVED', '已解決'), ('DISMISSED', '已駁回')]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    target_type = models.CharField("目標類型", max_length=20, choices=TARGET_CHOICES)
    target_listing_id = models.IntegerField("目標刊登ID", blank=True, null=True)
    target_user_id = models.IntegerField("目標使用者ID", blank=True, null=True)
    reason_code = models.CharField("檢舉原因代碼", max_length=50)
    detail = models.TextField("詳細說明", blank=True, null=True)
    status = models.CharField("狀態", max_length=20, choices=STATUS_CHOICES, default='OPEN')
    resolution_note = models.TextField("處理備註", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ModerationAction(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='actions')
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField("處置動作", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)