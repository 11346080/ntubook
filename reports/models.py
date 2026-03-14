from django.db import models
from accounts.models import CustomUser

class Report(models.Model):
    STATUS_CHOICES = [
        ('OPEN', '未處理'), ('IN_REVIEW', '審核中'),
        ('RESOLVED', '已解決'), ('DISMISSED', '已撤銷'),
    ]
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_reports', verbose_name='檢舉人')
    target_type = models.CharField('目標類型', max_length=20, choices=[('listing', '刊登'), ('user', '使用者')])
    target_listing_id = models.IntegerField('目標刊登ID', null=True, blank=True)
    target_user_id = models.IntegerField('目標使用者ID', null=True, blank=True)
    reason_code = models.CharField('檢舉原因', max_length=50)
    detail = models.TextField('補充說明', blank=True)
    status = models.CharField('處理狀態', max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField('建立時間', auto_now_add=True)

    class Meta:
        verbose_name = '檢舉紀錄'
        verbose_name_plural = '1. 檢舉紀錄'

class ModerationAction(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='actions', verbose_name='關聯檢舉')
    moderator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='審核人員')
    action_taken = models.CharField('處置動作', max_length=50) # warn, require_edit, force_remove, ban_user
    resolution_note = models.TextField('處理備註', blank=True)
    created_at = models.DateTimeField('處理時間', auto_now_add=True)

    class Meta:
        verbose_name = '審核處置紀錄'
        verbose_name_plural = '2. 審核處置紀錄'