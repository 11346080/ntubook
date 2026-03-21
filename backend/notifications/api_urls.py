from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.notification_list_api, name='api-notification-list'),
]
