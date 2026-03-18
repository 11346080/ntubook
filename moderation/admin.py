from django.contrib import admin
from django.utils.html import format_html

from .models import Report, ModerationAction
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


def mark_in_review(modeladmin, request, queryset):
    updated = queryset.update(status=Report.Status.IN_REVIEW)
    modeladmin.message_user(request, f'{updated} 件檢舉已設為「審查中」。')


def mark_resolved(modeladmin, request, queryset):
    from django.utils import timezone
    count = 0
    for report in queryset.filter(status__in=[Report.Status.OPEN, Report.Status.IN_REVIEW]):
        report.status = Report.Status.RESOLVED
        report.handled_by = request.user
        report.handled_at = timezone.now()
        report.save(update_fields=['status', 'handled_by', 'handled_at', 'updated_at'])
        count += 1
    modeladmin.message_user(request, f'{count} 件檢舉已標記為「已處理」。')


def mark_dismissed(modeladmin, request, queryset):
    updated = queryset.update(status=Report.Status.DISMISSED)
    modeladmin.message_user(request, f'{updated} 件檢舉已標記為「已駁回」。')


mark_in_review.short_description = '將所選檢舉設為「審查中」'
mark_resolved.short_description = '將所選檢舉「已處理」（含時間戳）'
mark_dismissed.short_description = '將所選檢舉「已駁回」'


@admin.action(description='移除刊登並連動 Report 為已處理')
def remove_listing_and_record(modeladmin, request, queryset):
    from listings.models import Listing
    from django.utils import timezone

    if not request.user.is_authenticated:
        modeladmin.message_user(request, '操作失敗：需要登入。', level='error')
        return

    listings_removed = 0
    actions_created = 0

    for report in queryset.select_related('target_listing', 'target_listing__book'):
        if report.target_type == Report.TargetType.LISTING and report.target_listing:
            listing = report.target_listing

            if listing.status != Listing.Status.REMOVED:
                listing.status = Listing.Status.REMOVED
                listing.off_shelf_reason = f'[檢舉 #{report.id}] 管理員移除'
                listing.save(update_fields=['status', 'off_shelf_reason', 'updated_at'])
                listings_removed += 1

            ModerationAction.objects.create(
                admin=request.user,
                action_type=ModerationAction.ActionType.REMOVE_LISTING,
                target_listing=listing,
                target_user=listing.seller,
                report=report,
                reason=f'[檢舉 #{report.id}] 管理員移除刊登',
            )
            actions_created += 1

            report.status = Report.Status.RESOLVED
            report.handled_by = request.user
            report.handled_at = timezone.now()
            report.resolution_note = f'已移除刊登 #{listing.id}'
            report.save(update_fields=[
                'status', 'handled_by', 'handled_at', 'resolution_note', 'updated_at'
            ])

    modeladmin.message_user(
        request,
        f'完成：移除 {listings_removed} 件刊登、建立 {actions_created} 筆 ModerationAction 紀錄。',
    )


@admin.display(description='目標摘要')
def target_summary(obj):
    if obj.target_type == Report.TargetType.LISTING and obj.target_listing:
        book = obj.target_listing.book
        return format_html(
            '<a href="/admin/listings/listing/{}/change/" target="_blank">{} (ID:{})</a>',
            obj.target_listing_id, book.title, obj.target_listing_id
        )
    elif obj.target_type == Report.TargetType.USER and obj.target_user:
        return format_html(
            '<a href="/admin/accounts/user/{}/change/" target="_blank">{} (ID:{})</a>',
            obj.target_user_id, obj.target_user.username, obj.target_user_id
        )
    return '-'


@admin.display(description='待處理案件')
def is_open_case(obj):
    if obj.status in (Report.Status.OPEN, Report.Status.IN_REVIEW):
        return format_html('<span style="color:#c00;font-weight:bold">待處理</span>')
    return format_html('<span style="color:green">{}</span>', obj.get_status_display())


@admin.display(description='檢舉狀態')
def status_badge(obj):
    status_map = {
        'OPEN': ('待處理', '#c00'),
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

    actions = [
        mark_in_review, mark_resolved, mark_dismissed,
        remove_listing_and_record, export_model_as_csv,
    ]


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
