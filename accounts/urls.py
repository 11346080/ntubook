from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),  # W4: FBV + @login_required 範例
    path('', include('django.contrib.auth.urls')),
]
