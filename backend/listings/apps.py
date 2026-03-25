from django.apps import AppConfig


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'
    verbose_name = '刊登管理'

    def ready(self):
        # 啟用 listings signals
        import listings.signals  # noqa: F401
        
        # 啟動後台審查排程器
        import os
        from django.conf import settings
        
        # 只在主進程啟動排程器（避免 runserver 雙引擎問題）
        if os.environ.get('RUN_MAIN') == 'true' or settings.DEBUG is False:
            try:
                from listings.scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                print(f'⚠️ 排程器啟動失敗: {str(e)}')
