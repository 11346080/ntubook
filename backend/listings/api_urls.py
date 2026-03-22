from django.urls import path
from . import views

urlpatterns = [
    # 具體路由必須放在前面，避免被參數路由匹配
    path('latest/', views.latest_listings_api, name='api-listing-latest'),
    path('<int:listing_id>/', views.listing_detail_api, name='api-listing-detail'),
    # 根路由：GET 列表，POST 建立新刊登
    path('', views.listing_list_or_create_api, name='api-listing-list-or-create'),
]
