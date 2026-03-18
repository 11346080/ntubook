from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='listing_list'),
    path('my/', views.MyListingListView.as_view(), name='my_listing_list'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
]
