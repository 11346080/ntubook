from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.OAuthEntryView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('first-login/', views.FirstLoginView.as_view(), name='first_login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
]
