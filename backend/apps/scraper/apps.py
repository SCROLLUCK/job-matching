from django.apps import AppConfig


class ScraperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scraper"

    def ready(self):
        from . import scheduler
        scheduler.start(interval_minutes=30)
