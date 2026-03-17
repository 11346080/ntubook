from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_code', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'type_code')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)