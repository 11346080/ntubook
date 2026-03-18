from django.contrib import admin
from .models import Report, ModerationAction


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'target_type', 'reason_code', 'status', 'created_at']
    search_fields = ['reporter__username', 'reason_code']
    list_filter = ['status', 'target_type', 'reason_code']


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'admin', 'action_type', 'target_user', 'target_listing', 'created_at']
    search_fields = ['admin__username', 'action_type']
    list_filter = ['action_type', 'created_at']
