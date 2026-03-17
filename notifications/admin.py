from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_code', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'type_code')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    list_per_page = 25
    actions = ['export_as_csv']

    @admin.action(description='匯出為 CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="notifications.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'user', 'type_code', 'title', 'message', 'related_listing_id', 'related_request_id', 'is_read', 'created_at'])
        for obj in queryset:
            writer.writerow([obj.id, obj.user.username, obj.type_code, obj.title, obj.message, obj.related_listing_id, obj.related_request_id, obj.is_read, obj.created_at])
        return response