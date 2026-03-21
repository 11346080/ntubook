from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.userprofile_list_api, name='api-userprofile-list'),
]
