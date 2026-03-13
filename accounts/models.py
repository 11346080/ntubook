from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    STATUS_CHOICES = [
        ('ACTIVE', '正常'),
        ('SUSPENDED', '停權'),
        ('RESTRICTED_LISTING', '限制刊登'),
    ]
    account_status = models.CharField("帳號狀態", max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField("暱稱", max_length=50)
    student_no = models.CharField("學號", max_length=20, blank=True, null=True)
    
    # 關聯到 core 的學校資料
    program_type = models.ForeignKey('core.ProgramType', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True, blank=True)
    class_group = models.ForeignKey('core.ClassGroup', on_delete=models.SET_NULL, null=True, blank=True)
    
    grade_no = models.IntegerField("年級", blank=True, null=True)
    contact_email = models.EmailField("聯絡信箱", blank=True, null=True)
    avatar_url = models.URLField("頭像連結", blank=True, null=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    def __str__(self):
        return f"{self.display_name} 的個人資料"