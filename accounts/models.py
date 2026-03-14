from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import ProgramType, Department, ClassGroup

class CustomUser(AbstractUser):
    ACCOUNT_STATUS_CHOICES = [
        ('ACTIVE', '啟用'),
        ('SUSPENDED', '停權'),
        ('RESTRICTED_LISTING', '限制刊登'),
    ]
    account_status = models.CharField('帳號狀態', max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='ACTIVE')

    class Meta:
        verbose_name = '使用者帳號'
        verbose_name_plural = '1. 使用者帳號'

    # 衍生欄位：快速判斷是否被停權
    @property
    def is_suspended(self):
        return self.account_status == 'SUSPENDED'

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', verbose_name='關聯帳號')
    display_name = models.CharField('顯示暱稱', max_length=50)
    student_no = models.CharField('學號', max_length=20, blank=True, null=True)
    program_type = models.ForeignKey(ProgramType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='學制')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='系所')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='班級')
    grade_no = models.PositiveSmallIntegerField('年級', choices=[(i, f'{i}年級') for i in range(1, 6)], null=True, blank=True)
    contact_email = models.EmailField('聯絡信箱', blank=True, null=True)
    avatar_url = models.URLField('頭像連結', blank=True, null=True)

    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '2. 使用者資料'

    def __str__(self):
        return self.display_name