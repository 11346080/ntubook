from django.db import models
from django.contrib import admin
from .models import Listing, ListingImage,  BookFavorite

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('book', 'seller', 'used_price', 'condition_level', 'status', 'created_at')
    list_filter = ('status', 'condition_level', 'origin_term')
    search_fields = ('book__title', 'seller__username', 'seller__profile__display_name')
    inlines = [ListingImageInline]
    ordering = ('-created_at',)
    actions = ['make_off_shelf', 'export_as_csv']
    
    # 編輯頁面的表單區塊分組
    fieldsets = (
        ('商品核心資訊', {
            'fields': ('book', 'seller', 'status')
        }),
        ('定價與書況', {
            'fields': ('used_price', 'condition_level', 'description', 'seller_note')
        }),
        ('原始課程資訊', {
            'fields': ('origin_academic_year', 'origin_term', 'origin_class_group')
        }),
        ('時間紀錄', {
            'fields': ('deleted_at',),
            'classes': ('collapse',) # 預設折疊起來，保持畫面乾淨
        }),
    )

    @admin.action(description='批次將選取的刊登強制下架')
    def make_off_shelf(self, request, queryset):
        # 這裡也可以透過 signal 連動下架時間
        updated = queryset.update(status='OFF_SHELF')
        self.message_user(request, f'成功將 {updated} 筆刊登強制下架。')

    @admin.action(description='匯出為 CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="listings.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'book_title', 'seller', 'used_price', 'condition_level', 'status', 'created_at'])
        for obj in queryset:
            writer.writerow([obj.id, obj.book.title, obj.seller.username, obj.used_price, obj.condition_level, obj.status, obj.created_at])
        return response

@admin.register(BookFavorite)
class BookFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title')