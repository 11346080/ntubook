from django.urls import path
from . import views
from .notifications_api import (
    notifications_list_api,
    notifications_unread_count_api,
    notification_read_api,
    notifications_read_all_api,
    notification_delete_api,
    notifications_delete_all_api
)

urlpatterns = [
    # 原有路由
    path('list/', views.notification_list_api, name='api-notification-list'),
    
    # 新增路由 (使用新的 notifications_api.py 中的視圖)
    path('', notifications_list_api, name='api-notifications-list'),
    path('unread-count/', notifications_unread_count_api, name='api-notifications-unread-count'),
    path('<int:notification_id>/read/', notification_read_api, name='api-notification-read'),
    path('read-all/', notifications_read_all_api, name='api-notifications-read-all'),
    path('<int:notification_id>/delete/', notification_delete_api, name='api-notification-delete'),
    path('delete-all/', notifications_delete_all_api, name='api-notifications-delete-all'),
]
