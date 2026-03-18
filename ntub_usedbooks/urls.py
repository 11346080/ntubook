from django.contrib import admin
from django.urls import path

from . import views
from . import admin as ntub_admin

urlpatterns = [
    path('admin/', ntub_admin.ntub_admin_site.urls),
    path('', views.home, name='home'),
]
