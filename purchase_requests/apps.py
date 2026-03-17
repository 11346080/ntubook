from django.apps import AppConfig

class PurchaseRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase_requests'
    verbose_name = '預約流程管理'

    def ready(self):
        import purchase_requests.signals # 啟動訊號