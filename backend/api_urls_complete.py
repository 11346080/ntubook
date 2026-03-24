"""
完整 API URL 配置 / Complete API URL Configuration
整合所有應用的 API 路由
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Accounts / 帳戶管理
from accounts.api_views import me_api, user_profile_api, create_profile_api

# Listings / 刊登管理
from listings import views as listing_views
from listings.listing_actions_api import (
    accept_purchase_request,
    reject_purchase_request, 
    cancel_purchase_request,
    listing_off_shelf,
    listing_mark_sold,
    listing_relist
)

# Books / 書籍管理
from books import views as book_views

# Purchase Requests / 預約管理
from purchase_requests import views as purchase_request_views

# Notifications / 通知管理
from notifications.notifications_api import (
    notifications_list_api,
    notifications_unread_count_api,
    notification_read_api,
    notifications_read_all_api,
    notification_delete_api,
    notifications_delete_all_api
)

# Moderation / 舉報管理
from moderation.reports_api import (
    create_report_api,
    my_reports_api,
    report_detail_api,
    report_update_status_api
)

urlpatterns = [
    # ============================================================================
    # 1. 認證相關 / Authentication
    # ============================================================================
    path('auth/token/', TokenObtainPairView.as_view(), name='api-token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    
    # ============================================================================
    # 2. 用戶帳戶相關 / User Account
    # ============================================================================
    path('me/', me_api, name='api-me'),
    path('me/profile/', user_profile_api, name='api-me-profile'),
    path('me/profile/create/', create_profile_api, name='api-me-profile-create'),
    
    # ============================================================================
    # 3. 書籍相關 / Books
    # ============================================================================
    path('books/', book_views.book_list_api, name='api-books-list'),
    path('books/<int:book_id>/', book_views.book_detail_api, name='api-books-detail'),
    path('books/<int:book_id>/favorite/', book_views.toggle_favorite_api, name='api-toggle-favorite'),
    
    # ============================================================================
    # 4. 刊登相關 / Listings
    # ============================================================================
    
    # 列表和搜尋
    path('listings/', listing_views.listing_list_api, name='api-listings-list'),
    path('listings/my-listings/', listing_views.my_listings_api, name='api-my-listings'),
    path('listings/latest/', listing_views.latest_listings_api, name='api-latest-listings'),
    path('listings/recommended/', listing_views.recommended_listings_api, name='api-recommended-listings'),
    
    # 刊登詳情和操作
    path('listings/<int:listing_id>/', listing_views.listing_detail_api, name='api-listing-detail'),
    path('listings/<int:listing_id>/requests/', listing_views.create_purchase_request_for_listing, name='api-listing-requests'),
    path('listings/<int:listing_id>/off_shelf/', listing_off_shelf, name='api-listing-off-shelf'),
    path('listings/<int:listing_id>/mark_sold/', listing_mark_sold, name='api-listing-mark-sold'),
    path('listings/<int:listing_id>/relist/', listing_relist, name='api-listing-relist'),
    
    # 預約請求管理
    path('requests/<int:request_id>/accept/', accept_purchase_request, name='api-request-accept'),
    path('requests/<int:request_id>/reject/', reject_purchase_request, name='api-request-reject'),
    path('requests/<int:request_id>/cancel/', cancel_purchase_request, name='api-request-cancel'),
    
    # ============================================================================
    # 5. 預約相關 / Purchase Requests
    # ============================================================================
    path('purchase-requests/', purchase_request_views.purchaserequest_list_api, name='api-purchase-requests-list'),
    path('purchase-requests/my-requests/', purchase_request_views.my_requests_api, name='api-my-requests'),
    path('purchase-requests/<int:purchase_request_id>/', purchase_request_views.purchaserequest_detail_api, name='api-purchase-request-detail'),
    
    # ============================================================================
    # 6. 通知相關 / Notifications
    # ============================================================================
    path('notifications/', notifications_list_api, name='api-notifications-list'),
    path('notifications/unread-count/', notifications_unread_count_api, name='api-notifications-unread-count'),
    path('notifications/<int:notification_id>/read/', notification_read_api, name='api-notification-read'),
    path('notifications/read-all/', notifications_read_all_api, name='api-notifications-read-all'),
    path('notifications/<int:notification_id>/delete/', notification_delete_api, name='api-notification-delete'),
    path('notifications/delete-all/', notifications_delete_all_api, name='api-notifications-delete-all'),
    
    # ============================================================================
    # 7. 舉報相關 / Reports
    # ============================================================================
    path('reports/', create_report_api, name='api-reports-create'),
    path('reports/my-reports/', my_reports_api, name='api-my-reports'),
    path('reports/<int:report_id>/', report_detail_api, name='api-report-detail'),
    path('reports/<int:report_id>/status/', report_update_status_api, name='api-report-update-status'),
    
    # ============================================================================
    # 8. 收藏相關 / Favorites
    # ============================================================================
    path('favorites/', book_views.favorite_list_api, name='api-favorites-list'),
    
    # ============================================================================
    # 9. 搜尋和過濾 / Search and Filters
    # ============================================================================
    path('search/', listing_views.search_listings_api, name='api-search'),
]

api_urlpatterns = [
    # 這個列表用於主 urls.py 的參考
    # This list is for reference in main urls.py
]
