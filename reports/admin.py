from django.contrib import admin
from .models import Report, ModerationAction

class ModerationActionInline(admin.StackedInline):
    model = ModerationAction
    extra = 1

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'target_type', 'reason_code', 'status', 'created_at')
    list_filter = ('status', 'target_type', 'reason_code')
    search_fields = ('reporter__username', 'detail')
    inlines = [ModerationActionInline]
    ordering = ('-created_at',)
    list_per_page = 25
    actions = ['mark_as_resolved', 'mark_as_dismissed', 'export_as_csv']

    @admin.action(description='批次標記為「已解決」')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')

    @admin.action(description='批次標記為「已撤銷」')
    def mark_as_dismissed(self, request, queryset):
        queryset.update(status='DISMISSED')

    @admin.action(description='匯出為 CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reports.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'reporter', 'target_type', 'target_listing_id', 'target_user_id', 'reason_code', 'detail', 'status', 'created_at'])
        for obj in queryset:
            writer.writerow([obj.id, obj.reporter.username, obj.target_type, obj.target_listing_id, obj.target_user_id, obj.reason_code, obj.detail, obj.status, obj.created_at])
        return response