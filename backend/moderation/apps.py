from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moderation'
    verbose_name = '審核管理'

    def ready(self):
        # 啟用 moderation signals
        import moderation.signals  # noqa: F401
