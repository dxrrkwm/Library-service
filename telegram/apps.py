from django.apps import AppConfig


class TelegramConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram"

    def ready(self):
        import telegram.signals  # noqa
