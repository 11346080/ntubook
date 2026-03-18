from django.contrib import admin
from django.utils.html import format_html

from .models import Report, ModerationAction
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


def mark_in_review(modeladmin, request, queryset):
    queryset.update(status=Report.Status.IN_REVIEW)


def mark_resolved(modeladmin, request, queryset):
    queryset.update(status=Report.Status.RESOLVED)


def mark_dismissed(modeladmin, request, queryset):
    queryset.update(status=Report.Status.DISMISSED)


mark_in_review.short_description = '將所選檢舉設為「審查中」'
mark_resolved.short_description = '將所選檢舉「已處理」'
mark_dismissed.short_description = '將所選檢舉「已駁回」'


@admin.display(description='目標摘要')
def target_summary(obj):
    if obj.target_type == Report.TargetType.LISTING and obj.target_listing:
        book = obj.target_listing.book
        return format_html(
            '<a href="/admin/listings/listing/{}/change/">{} (ID:{})</a>',
            obj.target_listing_id, book.title, obj.target_listing_id
        )
    elif obj.target_type == Report.TargetType.USER and obj.target_user:
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{} (ID:{})</a>',
            obj.target_user_id, obj.target_user.username, obj.target_user_id
        )
    return '-'


@admin.display(description='待處理案件')
def is_open_case(obj):
    if obj.status in (Report.Status.OPEN, Report.Status.IN_REVIEW):
        return format_html('<span style="color:#c60;font-weight:bold">待處理</span>')
    return format_html('<span style="color:green">{}</span>', obj.get_status_display())


@admin.display(description='檢舉狀態')
def status_badge(obj):
    status_map = {
        'OPEN': ('待處理', '#c60'),
        'IN_REVIEW': ('審查中', '#217dbb'),
        'RESOLVED': ('已處理', 'green'),
        'DISMISSED': ('已駁回', '#888'),
    }
    label, color = status_map.get(obj.status, (obj.status, 'black'))
    return format_html(
        '<span style="color:{};font-weight:bold">{}</span>', color, label
    )


class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reporter', 'target_type', 'reason_code',
        status_badge, is_open_case, target_summary,
        'risk_score', 'handled_by', 'created_at',
    ]
    list_display_links = ['id']
    list_select_related = ['reporter', 'handled_by']

    search_fields = [
        'reporter__username', 'reason_code', 'detail', 'resolution_note',
    ]
    list_filter = ['status', 'target_type', 'reason_code', 'created_at']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'handled_at']

    raw_id_fields = ['reporter', 'target_listing', 'target_user', 'handled_by']

    fieldsets = (
        ('檢舉人', {
            'fields': ('reporter',),
        }),
        ('檢舉目標', {
            'fields': ('target_type', 'target_listing', 'target_user'),
        }),
        ('檢舉內容', {
            'fields': ('reason_code', 'detail'),
        }),
        ('狀態與處置', {
            'fields': ('status', 'handled_by', 'handled_at', 'resolution_note', 'risk_score'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [mark_in_review, mark_resolved, mark_dismissed, export_model_as_csv]


class ModerationActionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'admin', 'action_type',
        'target_user', 'target_listing', 'report',
        'created_at',
    ]
    list_display_links = ['id']
    list_select_related = ['admin', 'target_user', 'report']

    search_fields = ['admin__username', 'reason']
    list_filter = ['action_type', 'created_at']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at']

    raw_id_fields = ['admin', 'target_user', 'target_listing', 'report']

    fieldsets = (
        ('基本資訊', {
            'fields': ('admin', 'action_type'),
        }),
        ('目標', {
            'fields': ('target_user', 'target_listing', 'report'),
        }),
        ('處置原因', {
            'fields': ('reason',),
        }),
        ('時間戳記', {
            'fields': ('created_at',),
        }),
    )

    actions = [export_model_as_csv]


ntub_admin_site.register(Report, ReportAdmin)
ntub_admin_site.register(ModerationAction, ModerationActionAdmin)
