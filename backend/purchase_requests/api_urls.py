from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchaserequest_list_api, name='api-purchaserequest-list'),
    path('list/', views.purchaserequest_list_api, name='api-purchase-requests-list'),
    path('my-requests/', views.my_requests_api, name='api-my-requests'),
]
