from django.apps import AppConfig


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'
    verbose_name = '刊登管理'

    def ready(self):
        # 啟用 listings signals
        import listings.signals  # noqa: F401
