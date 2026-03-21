from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.listing_list_api, name='api-listing-list'),
]
