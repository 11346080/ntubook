from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """通知列表頁"""
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtered_notifications'] = self.get_queryset().filter(is_read=False)
        return ctx
