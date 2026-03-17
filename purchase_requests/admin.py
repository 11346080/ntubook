from django.contrib import admin
from .models import PurchaseRequest

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('listing__book__title', 'buyer__username', 'buyer__email')
    readonly_fields = ('created_at', 'risk_score')
    ordering = ('-created_at',)
    list_per_page = 25
    # 讓管理員可以快速在後台改狀態測試
    list_editable = ('status',)