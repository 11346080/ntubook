from django.urls import path
from . import views

app_name = 'purchase_requests'

urlpatterns = [
    path('', views.PurchaseRequestListView.as_view(), name='request_list'),
    path('<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='request_detail'),
    path('<int:pk>/accept/', views.accept_request, name='request_accept'),
    path('<int:pk>/reject/', views.reject_request, name='request_reject'),
    path('<int:pk>/cancel/', views.cancel_request, name='request_cancel'),
]
