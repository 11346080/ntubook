from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type_code', 'title', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_filter = ['is_read', 'type_code', 'created_at']
