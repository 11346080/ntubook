from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include('django.contrib.auth.urls')),
]
