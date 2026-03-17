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

    actions = ['export_as_csv']

    @admin.action(description='匯出為 CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchase_requests.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'listing', 'buyer', 'status', 'buyer_message', 'risk_score', 'expires_at', 'created_at', 'responded_at'])
        for obj in queryset:
            writer.writerow([obj.id, obj.listing.book.title, obj.buyer.username, obj.status, obj.buyer_message, obj.risk_score, obj.expires_at, obj.created_at, obj.responded_at])
        return response