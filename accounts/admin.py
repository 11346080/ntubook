from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import User, UserProfile
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


@admin.display(description='暱稱')
def profile_display_name(obj):
    try:
        return obj.profile.display_name
    except UserProfile.DoesNotExist:
        return '-'


@admin.display(description='帳號完整度')
def profile_completed(obj):
    try:
        p = obj.profile
        filled = sum([
            bool(p.display_name),
            bool(p.student_no),
            bool(p.program_type),
            bool(p.department),
            bool(p.class_group),
        ])
        return f'{int(filled / 5 * 100)}%  ({filled}/5)'
    except UserProfile.DoesNotExist:
        return '未建立'


@admin.display(description='角色摘要')
def role_summary(obj):
    parts = []
    if obj.is_superuser:
        parts.append('超級管理員')
    elif obj.is_staff:
        parts.append('站務人員')
    else:
        parts.append('一般會員')

    status_map = {
        'ACTIVE': '正常',
        'SUSPENDED': '停權',
        'RESTRICTED_LISTING': '限制刊登',
    }
    status_label = status_map.get(obj.account_status, obj.account_status)
    parts.append(f'[{status_label}]')
    return ' '.join(parts)


@admin.display(description='狀態')
def status_badge(obj):
    status_map = {
        'ACTIVE': ('正常', 'color:green;font-weight:bold'),
        'SUSPENDED': ('停權', 'color:red;font-weight:bold'),
        'RESTRICTED_LISTING': ('限制刊登', 'color:#c60;font-weight:bold'),
    }
    label, style = status_map.get(obj.account_status, (obj.account_status, ''))
    return format_html('<span style="{}">{}</span>', style, label)


@admin.action(description='將所選帳號設為「正常」')
def make_active(modeladmin, request, queryset):
    queryset.update(account_status=User.AccountStatus.ACTIVE)


@admin.action(description='將所選帳號設為「停權」')
def make_suspended(modeladmin, request, queryset):
    queryset.update(account_status=User.AccountStatus.SUSPENDED)


@admin.action(description='將所選帳號設為「限制刊登」')
def make_restricted_listing(modeladmin, request, queryset):
    queryset.update(account_status=User.AccountStatus.RESTRICTED_LISTING)


class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', profile_display_name, 'email',
        'account_status', status_badge, 'is_staff', 'is_superuser', 'is_active',
        profile_completed, role_summary, 'created_at',
    ]
    list_display_links = ['username']

    search_fields = ['username', 'email', 'google_sub']
    list_filter = [
        'account_status', 'auth_provider', 'is_staff', 'is_superuser', 'is_active',
    ]

    ordering = ['-created_at']
    list_per_page = 50

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
        ('個人資訊', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('權限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
        }),
        ('驗證資訊', {
            'fields': ('google_sub', 'auth_provider'),
        }),
        ('帳號狀態', {
            'fields': ('account_status', 'account_status_reason'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [
        make_active, make_suspended, make_restricted_listing,
        export_model_as_csv,
    ]


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'display_name', 'student_no',
        'program_type', 'department', 'class_group', 'grade_no', 'created_at',
    ]
    search_fields = ['user__username', 'user__email', 'display_name', 'student_no']
    list_filter = ['program_type', 'department', 'grade_no']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']

    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'display_name', 'student_no'),
        }),
        ('學籍資訊', {
            'fields': ('program_type', 'department', 'class_group', 'grade_no'),
        }),
        ('聯絡方式', {
            'fields': ('contact_email', 'avatar_url'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


ntub_admin_site.register(User, UserAdmin)
ntub_admin_site.register(UserProfile, UserProfileAdmin)
ntub_admin_site.register(Group, BaseGroupAdmin)
