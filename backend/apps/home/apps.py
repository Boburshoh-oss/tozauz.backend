from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home"
    verbose_name = "Uy boshqaruvi"

    def ready(self):
        """App tayyor bo'lganda signallarni import qilish"""
        import apps.home.signals
     