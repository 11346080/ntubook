from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(LoginRequiredMixin, ListView):
    """通知列表頁"""
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# ================= API Views =================


@api_view(['GET'])
def notification_list_api(request):
    """取得所有通知的 JSON API 端點 / Get all notifications API endpoint"""
    notifications = Notification.objects.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

