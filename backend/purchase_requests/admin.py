from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import PurchaseRequest
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


def mark_accepted(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('listing', 'listing__book', 'buyer'):
        if obj.status != PurchaseRequest.Status.ACCEPTED:
            obj.status = PurchaseRequest.Status.ACCEPTED
            obj.responded_at = timezone.now()
            obj.contact_released_at = timezone.now()
            obj.save(update_fields=['status', 'responded_at', 'contact_released_at', 'updated_at'])
            count += 1
    modeladmin.message_user(request, f'{count} 件請求已標記為「已接受」（含時間戳）。')


def mark_rejected(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('listing', 'listing__book', 'buyer'):
        if obj.status != PurchaseRequest.Status.REJECTED:
            obj.status = PurchaseRequest.Status.REJECTED
            obj.responded_at = timezone.now()
            obj.save(update_fields=['status', 'responded_at', 'updated_at'])
            count += 1
    modeladmin.message_user(request, f'{count} 件請求已標記為「已拒絕」（含時間戳）。')


def mark_expired(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('listing', 'listing__book', 'buyer'):
        if obj.status not in (PurchaseRequest.Status.EXPIRED,):
            obj.status = PurchaseRequest.Status.EXPIRED
            obj.save(update_fields=['status', 'updated_at'])
            count += 1
    modeladmin.message_user(request, f'{count} 件請求已標記為「已過期」。')


mark_accepted.short_description = '將所選請求標記為「已接受」（含時間戳）'
mark_rejected.short_description = '將所選請求標記為「已拒絕」（含時間戳）'
mark_expired.short_description = '將所選請求標記為「已過期」'


@admin.display(description='已過期')
def is_expired(obj):
    if obj.expires_at and obj.expires_at < timezone.now():
        return format_html('<span style="color:red;font-weight:bold">是</span>')
    return format_html('<span style="color:green">否</span>')


@admin.display(description='已有回應')
def has_response(obj):
    if obj.status != PurchaseRequest.Status.PENDING:
        return format_html('<span style="color:green;font-weight:bold">是</span>')
    return format_html('<span style="color:#888">否</span>')


@admin.display(description='聯絡資訊已開放')
def contact_released(obj):
    if obj.contact_released_at:
        return format_html('<span style="color:green">是</span>')
    return format_html('<span style="color:#888">否</span>')


@admin.display(description='請求狀態')
def status_badge(obj):
    status_map = {
        'PENDING': ('等待中', '#217dbb'),
        'ACCEPTED': ('已接受', 'green'),
        'REJECTED': ('已拒絕', '#c00'),
        'CANCELLED_BY_BUYER': ('買家取消', '#888'),
        'CANCELLED_BY_SELLER': ('賣家取消', '#888'),
        'EXPIRED': ('已過期', 'red'),
    }
    label, color = status_map.get(obj.status, (obj.status, 'black'))
    return format_html(
        '<span style="color:{};font-weight:bold">{}</span>', color, label
    )


class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'listing', 'buyer', status_badge,
        is_expired, has_response, contact_released,
        'expires_at', 'created_at',
    ]
    list_display_links = ['id']
    list_select_related = ['listing', 'listing__book', 'buyer']

    search_fields = [
        'listing__book__title', 'listing__book__isbn13',
        'buyer__username', 'buyer_message',
    ]
    list_filter = ['status', 'created_at', 'responded_at', 'cancelled_at']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = [
        'created_at', 'updated_at', 'responded_at', 'cancelled_at', 'contact_released_at',
    ]

    raw_id_fields = ['listing', 'buyer']

    fieldsets = (
        ('基本資訊', {
            'fields': ('listing', 'buyer', 'status'),
        }),
        ('買家留言', {
            'fields': ('buyer_message',),
        }),
        ('風險評估', {
            'fields': ('risk_score',),
        }),
        ('時間控制', {
            'fields': ('expires_at', 'responded_at', 'cancelled_at', 'contact_released_at'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [mark_accepted, mark_rejected, mark_expired, export_model_as_csv]


ntub_admin_site.register(PurchaseRequest, PurchaseRequestAdmin)
