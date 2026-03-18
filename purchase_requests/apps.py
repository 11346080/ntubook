from django.apps import AppConfig


class PurchaseRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase_requests'
    verbose_name = '預約請求管理'

    def ready(self):
        # 啟用 purchase_requests signals
        import purchase_requests.signals  # noqa: F401
