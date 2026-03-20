from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.OAuthEntryView.as_view(), name='login'),
    path('first-login/', views.FirstLoginView.as_view(), name='first_login'),
]
