from django.contrib import admin
from django.urls import path, include

from . import views
from . import admin as ntub_admin

urlpatterns = [
    path('admin/', ntub_admin.ntub_admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('notifications/', include('notifications.urls')),
    path('', views.home, name='home'),
]
