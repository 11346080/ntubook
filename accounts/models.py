from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for NTUB Used Books platform."""

    class AccountStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', '正常'
        SUSPENDED = 'SUSPENDED', '停權'
        RESTRICTED_LISTING = 'RESTRICTED_LISTING', '限制刊登'

    # email: 第一階段先沿用 AbstractUser 預設（nullable, non-unique）
    #        實際：Django 預設 EmailField 為 blank=True, null=False（ORM 層允許空白）
    #        資料庫層：users_user.email 目前無 UNIQUE 約束
    #        第二階段（0004）再加入 unique=True
    email = models.EmailField(
        max_length=254,
        blank=True,
        verbose_name='校內信箱'
    )

    # google_sub: 第一階段設為 nullable（null=True, blank=True, unique=True）
    #             第二階段（0004）再改為 not null
    google_sub = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Google 主體識別碼'
    )

    auth_provider = models.CharField(
        max_length=20,
        default='GOOGLE',
        verbose_name='驗證來源'
    )

    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name='帳號狀態'
    )

    account_status_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='狀態原因'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新時間'
    )

    class Meta:
        db_table = 'users_user'
        indexes = [
            models.Index(fields=['account_status'], name='users_user_status_idx'),
        ]

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """使用者個人檔 / User Profile"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='使用者'
    )
    display_name = models.CharField(max_length=50, verbose_name='顯示名稱')
    student_no = models.CharField(max_length=20, blank=True, null=True, verbose_name='學號')
    program_type = models.ForeignKey(
        'core.ProgramType',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='user_profiles',
        verbose_name='學制'
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='user_profiles',
        verbose_name='系所'
    )
    class_group = models.ForeignKey(
        'core.ClassGroup',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='user_profiles',
        verbose_name='班級'
    )
    grade_no = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='年級')
    contact_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='聯絡信箱')
    avatar_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='頭像網址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '使用者個人檔'
        verbose_name_plural = '使用者個人檔'
        indexes = [
            models.Index(fields=['program_type', 'department', 'class_group'], name='user_profiles_prog_dept_idx'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.display_name}"
