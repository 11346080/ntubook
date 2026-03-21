from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.report_list_api, name='api-report-list'),
]
