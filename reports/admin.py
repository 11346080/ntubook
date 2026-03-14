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
    actions = ['mark_as_resolved', 'mark_as_dismissed']

    @admin.action(description='批次標記為「已解決」')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')

    @admin.action(description='批次標記為「已撤銷」')
    def mark_as_dismissed(self, request, queryset):
        queryset.update(status='DISMISSED')