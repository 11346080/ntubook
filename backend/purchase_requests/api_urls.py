from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.purchaserequest_list_api, name='api-purchaserequest-list'),
]
