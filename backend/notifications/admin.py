from django.contrib import admin
from django.utils.html import strip_tags, format_html

from .models import Notification
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


def mark_as_read(modeladmin, request, queryset):
    updated = queryset.update(is_read=True)
    modeladmin.message_user(request, f'{updated} 筆通知已標記為已讀。')


def mark_as_unread(modeladmin, request, queryset):
    updated = queryset.update(is_read=False)
    modeladmin.message_user(request, f'{updated} 筆通知已標記為未讀。')


mark_as_read.short_description = '將所選通知標記為「已讀」'
mark_as_unread.short_description = '將所選通知標記為「未讀」'


@admin.display(description='訊息（前 40 字）')
def short_message(obj):
    msg = strip_tags(obj.message)
    return msg[:40] + '...' if len(msg) > 40 else msg


@admin.display(description='關聯物件')
def related_object_summary(obj):
    parts = []
    if obj.related_listing_id:
        parts.append(f'刊登 #{obj.related_listing_id}')
    if obj.related_request_id:
        parts.append(f'請求 #{obj.related_request_id}')
    return ', '.join(parts) if parts else '-'


@admin.display(description='是否已讀')
def is_read_badge(obj):
    if obj.is_read:
        return format_html('<span style="color:green;font-weight:bold">已讀</span>')
    return format_html('<span style="color:#c00">未讀</span>')


class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'type_code', 'title',
        short_message, is_read_badge,
        'related_listing', related_object_summary, 'created_at',
    ]
    list_display_links = ['id']
    list_select_related = ['user']

    search_fields = ['user__username', 'title', 'message', 'type_code']
    list_filter = ['is_read', 'type_code', 'created_at']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'read_at']

    raw_id_fields = ['user', 'related_listing', 'related_request']

    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'type_code', 'title', 'message'),
        }),
        ('關聯物件', {
            'fields': ('related_listing', 'related_request'),
        }),
        ('閱讀狀態', {
            'fields': ('is_read', 'read_at'),
        }),
        ('時間戳記', {
            'fields': ('created_at',),
        }),
    )

    actions = [mark_as_read, mark_as_unread, export_model_as_csv]


ntub_admin_site.register(Notification, NotificationAdmin)
