from django.contrib import admin
from django.utils.html import format_html

from .forms import BookForm
from .models import Book, BookApplicability, BookFavorite
from ntub_usedbooks.admin import ntub_admin_site
from ntub_usedbooks.admin_utils import export_model_as_csv


def mark_metadata_confirmed(modeladmin, request, queryset):
    count = queryset.update(metadata_status=Book.MetadataStatus.MANUALLY_CONFIRMED)
    modeladmin.message_user(request, f'{count} 本書籍已標記為「已確認」。')


def mark_needs_review(modeladmin, request, queryset):
    count = queryset.update(metadata_status=Book.MetadataStatus.NEEDS_REVIEW)
    modeladmin.message_user(request, f'{count} 本書籍已標記為「需審核」。')


mark_metadata_confirmed.short_description = '將所選書籍標記為「已確認」'
mark_needs_review.short_description = '將所選書籍標記為「需審核」'


@admin.display(description='ISBN')
def isbn_display(obj):
    return f'ISBN13: {obj.isbn13}' if obj.isbn13 else f'ISBN10: {obj.isbn10 or "-"}'


@admin.display(description='適用數')
def applicability_count(obj):
    return obj.applicabilities.count()


@admin.display(description='收藏數')
def favorite_count(obj):
    return obj.favorites.count()


@admin.display(description='資料狀態')
def metadata_status_display(obj):
    status_map = {
        'MANUALLY_CONFIRMED': ('已確認', 'green'),
        'NEEDS_REVIEW': ('需審核', '#c60'),
    }
    label, color = status_map.get(obj.metadata_status, (obj.metadata_status, 'black'))
    return format_html(
        '<span style="color:{};font-weight:bold">{}</span>',
        color, label
    )


class BookApplicabilityInline(admin.TabularInline):
    model = BookApplicability
    extra = 0
    raw_id_fields = ['class_group', 'source_listing']
    fields = ['academic_year', 'term', 'class_group', 'source_type', 'source_listing']
    show_change_link = True


class BookAdmin(admin.ModelAdmin):
    form = BookForm

    list_display = [
        'id', isbn_display, 'title', 'author_display', 'publisher',
        'metadata_source', metadata_status_display,
        applicability_count, favorite_count, 'created_at',
    ]
    list_display_links = ['id', 'title']

    search_fields = ['isbn13', 'isbn10', 'title', 'author_display', 'publisher']
    list_filter = ['metadata_source', 'metadata_status', 'language_code']
    ordering = ['title']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'publication_date_text']

    inlines = [BookApplicabilityInline]

    fieldsets = (
        ('ISBN 識別', {
            'fields': ('isbn13', 'isbn10'),
        }),
        ('書目基本資訊', {
            'fields': ('title', 'author_display', 'publisher'),
        }),
        ('出版資訊', {
            'fields': ('publication_year', 'publication_date_text', 'edition', 'language_code'),
        }),
        ('視覺資訊', {
            'fields': ('cover_image_url',),
        }),
        ('資料管理', {
            'fields': ('metadata_source', 'metadata_status'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [mark_metadata_confirmed, mark_needs_review, export_model_as_csv]


class BookApplicabilityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'book', 'academic_year', 'term',
        'class_group', 'source_type', 'created_at',
    ]
    search_fields = ['book__title', 'book__isbn13']
    list_filter = ['source_type', 'academic_year', 'term', 'class_group__program_type']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['book', 'class_group', 'source_listing']

    fieldsets = (
        ('基本資訊', {
            'fields': ('book', 'academic_year', 'term', 'class_group'),
        }),
        ('來源', {
            'fields': ('source_type', 'source_listing'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = [export_model_as_csv]


class BookFavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book', 'created_at']
    list_display_links = ['id']
    search_fields = ['user__username', 'book__title', 'book__isbn13']
    list_filter = ['book__metadata_status']
    ordering = ['-created_at']
    list_per_page = 50
    raw_id_fields = ['user', 'book']

    actions = [export_model_as_csv]


ntub_admin_site.register(Book, BookAdmin)
ntub_admin_site.register(BookApplicability, BookApplicabilityAdmin)
ntub_admin_site.register(BookFavorite, BookFavoriteAdmin)
