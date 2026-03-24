from django.urls import path
from . import views
from .reports_api import (
    create_report_api,
    my_reports_api,
    report_detail_api,
    report_update_status_api
)

urlpatterns = [
    # 原有路由
    path('list/', views.report_list_api, name='api-report-list'),
    
    # 新增路由 (使用新的 reports_api.py 中的視圖)
    path('', create_report_api, name='api-reports-create'),
    path('my-reports/', my_reports_api, name='api-my-reports'),
    path('<int:report_id>/', report_detail_api, name='api-report-detail'),
    path('<int:report_id>/status/', report_update_status_api, name='api-report-update-status'),
]
