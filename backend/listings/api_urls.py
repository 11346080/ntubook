from django.urls import path
from . import views

urlpatterns = [
    # 具體路由必須放在前面，避免被參數路由匹配
    path('latest/', views.latest_listings_api, name='api-listing-latest'),
    path('list/', views.listing_list_api, name='api-listing-list'),
]
