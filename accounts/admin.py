from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'google_sub', 'auth_provider',
        'account_status', 'account_status_reason', 'is_staff', 'is_active',
        'created_at', 'updated_at'
    ]
    search_fields = ['username', 'email', 'google_sub']
    list_filter = ['account_status', 'auth_provider', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('驗證資訊', {'fields': ('google_sub', 'auth_provider')}),
        ('帳號狀態', {'fields': ('account_status', 'account_status_reason')}),
        ('時間戳記', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'student_no', 'program_type', 'department', 'class_group', 'grade_no']
    search_fields = ['user__username', 'user__email', 'display_name', 'student_no']
    list_filter = ['program_type', 'department', 'grade_no']
