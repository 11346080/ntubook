from django.contrib import admin
from .models import Listing, ListingImage


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'book', 'used_price', 'condition_level', 'status', 'created_at']
    search_fields = ['book__title', 'book__isbn13', 'seller__username']
    list_filter = ['status', 'condition_level', 'created_at']


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'file_path', 'sort_order', 'is_primary', 'created_at']
    search_fields = ['listing__book__title', 'file_path']
    list_filter = ['is_primary']
