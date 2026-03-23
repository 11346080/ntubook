from django.contrib import admin
from django.utils.html import format_html

from .models import Listing, ListingImage
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv
from ntub_usedbooks.admin_helpers import update_status_with_timestamp


def make_available(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('seller', 'book'):
        if obj.status != Listing.Status.AVAILABLE:
            update_status_with_timestamp(obj, Listing.Status.AVAILABLE)
            count += 1
    modeladmin.message_user(request, f'{count} 件刊登已設為「可購買」。')


def make_off_shelf(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('seller', 'book'):
        if obj.status != Listing.Status.OFF_SHELF:
            update_status_with_timestamp(obj, Listing.Status.OFF_SHELF)
            count += 1
    modeladmin.message_user(request, f'{count} 件刊登已「下架」。')


def make_removed(modeladmin, request, queryset):
    count = 0
    for obj in queryset.select_related('seller', 'book'):
        if obj.status != Listing.Status.REMOVED:
            update_status_with_timestamp(obj, Listing.Status.REMOVED)
            count += 1
    modeladmin.message_user(request, f'{count} 件刊登已「移除」。')


make_available.short_description = '將所選刊登設為「可購買」（含時間戳）'
make_off_shelf.short_description = '將所選刊登「下架」（含時間戳）'
make_removed.short_description = '將所選刊登「移除」（含時間戳）'


@admin.display(description='圖片數')
def image_count(obj):
    return f'{obj.images.count()} 張'


@admin.display(description='已刪除')
def is_deleted(obj):
    if obj.deleted_at:
        return format_html('<span style="color:red;font-weight:bold">是</span>')
    return format_html('<span style="color:green">否</span>')


@admin.display(description='已保留')
def is_reserved(obj):
    if obj.status == Listing.Status.RESERVED:
        return format_html('<span style="color:#217dbb;font-weight:bold">是</span>')
    return format_html('<span style="color:#ccc">否</span>')


@admin.display(description='狀態摘要')
def visible_state_summary(obj):
    if obj.deleted_at:
        label = f'已刪除 ({obj.deleted_at.strftime("%m/%d")})'
        color = '#888'
    elif obj.status == Listing.Status.SOLD:
        label = '已售出'
        color = '#6a0dad'
    elif obj.status == Listing.Status.OFF_SHELF:
        label = '已下架'
        color = '#c60'
    elif obj.status == Listing.Status.REMOVED:
        label = '已移除'
        color = '#888'
    elif obj.status == Listing.Status.RESERVED:
        label = '已保留'
        color = '#217dbb'
    elif obj.status == Listing.Status.AVAILABLE:
        label = '可購買'
        color = 'green'
    else:
        label = obj.get_status_display()
        color = 'black'
    return format_html('<span style="color:{};font-weight:bold">{}</span>', color, label)


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ['file_name', 'mime_type', 'sort_order', 'is_primary', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


class ListingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'seller', 'book', 'used_price',
        'condition_level', 'status', visible_state_summary,
        image_count, is_deleted, 'created_at',
    ]
    list_display_links = ['id']
    list_select_related = ['seller', 'book']

    search_fields = [
        'book__title', 'book__isbn13', 'seller__username',
        'description',
    ]
    list_filter = [
        'status', 'condition_level',
        'created_at', 'sold_at', 'reserved_at',
    ]
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']

    raw_id_fields = ['seller', 'book', 'origin_class_group', 'deleted_by', 'accepted_request']

    inlines = [ListingImageInline]

    fieldsets = (
        ('核心刊登資訊', {
            'fields': ('seller', 'book', 'used_price', 'condition_level'),
        }),
        ('商品說明', {
            'fields': ('description', 'seller_note'),
        }),
        ('原使用資訊', {
            'fields': ('origin_academic_year', 'origin_term', 'origin_class_group'),
        }),
        ('狀態與風險', {
            'fields': ('status', 'off_shelf_reason', 'accepted_request', 'risk_score'),
        }),
        ('保留 / 售出', {
            'fields': ('reserved_at', 'sold_at'),
        }),
        ('軟刪除', {
            'fields': ('deleted_at', 'deleted_by'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [make_available, make_off_shelf, make_removed, export_model_as_csv]


class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'file_name', 'mime_type', 'sort_order', 'is_primary', 'created_at']
    list_display_links = ['id']
    list_select_related = ['listing', 'listing__book']
    search_fields = ['listing__book__title', 'file_name']
    list_filter = ['is_primary', 'listing__status']
    ordering = ['listing', 'sort_order']
    list_per_page = 100
    raw_id_fields = ['listing']

    actions = [export_model_as_csv]


ntub_admin_site.register(Listing, ListingAdmin)
ntub_admin_site.register(ListingImage, ListingImageAdmin)
