from django.contrib import admin
from django.urls import path, include

from . import views
from . import admin as ntub_admin

urlpatterns = [
    # ========== Admin ==========
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', ntub_admin.ntub_admin_site.urls),
    
    # ========== HTML Views (Traditional Routes) ==========
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('notifications/', include('notifications.urls')),
    path('requests/', include('purchase_requests.urls')),
    path('', views.home, name='home'),
    
    # ========== API Routes (Centralized under /api/) ==========
    path('api/accounts/', include('accounts.api_urls')),
    path('api/books/', include('books.api_urls')),
    path('api/core/', include('core.api_urls')),
    path('api/listings/', include('listings.api_urls')),
    path('api/moderation/', include('moderation.api_urls')),
    path('api/notifications/', include('notifications.api_urls')),
    path('api/requests/', include('purchase_requests.api_urls')),
]

