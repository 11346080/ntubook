from django.contrib import admin
from .models import PurchaseRequest


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'buyer', 'status', 'expires_at', 'created_at']
    search_fields = ['listing__book__title', 'buyer__username']
    list_filter = ['status', 'created_at']
