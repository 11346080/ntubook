from django.contrib import admin
from django.urls import path, include

from . import views
from . import admin as ntub_admin

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', ntub_admin.ntub_admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('notifications/', include('notifications.urls')),
    path('requests/', include('purchase_requests.urls')),
    path('', views.home, name='home'),
]
