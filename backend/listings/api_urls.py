from django.urls import path
from . import views
from .listing_actions_api import (
    accept_purchase_request,
    reject_purchase_request,
    cancel_purchase_request,
    listing_off_shelf,
    listing_mark_sold,
    listing_relist
)

urlpatterns = [
    # 具體路由必須放在前面，避免被參數路由匹配
    path('my-listings/', views.my_listings_api, name='api-listing-my-listings'),
    path('recommended/', views.recommended_listings_api, name='api-listing-recommended'),
    path('latest/', views.latest_listings_api, name='api-listing-latest'),
    
    # 刊登動作 / Listing Actions
    path('<int:listing_id>/requests/', views.create_purchase_request_for_listing, name='api-listing-requests'),
    path('<int:listing_id>/off_shelf/', listing_off_shelf, name='api-listing-off-shelf'),
    path('<int:listing_id>/mark_sold/', listing_mark_sold, name='api-listing-mark-sold'),
    path('<int:listing_id>/relist/', listing_relist, name='api-listing-relist'),
    
    # 預約請求管理 / Purchase Request Management
    path('requests/<int:request_id>/accept/', accept_purchase_request, name='api-request-accept'),
    path('requests/<int:request_id>/reject/', reject_purchase_request, name='api-request-reject'),
    path('requests/<int:request_id>/cancel/', cancel_purchase_request, name='api-request-cancel'),
    
    # 刊登詳情
    path('<int:listing_id>/', views.listing_detail_api, name='api-listing-detail'),
    
    # 根路由：GET 列表，POST 建立新刊登
    path('', views.listing_list_or_create_api, name='api-listing-list-or-create'),
]
