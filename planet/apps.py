from django.apps import AppConfig


class PlanetAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "planet"

    def ready(self):
        # Register configuration checks only after Django populates the app registry.
        from . import checks  # noqa: F401, PLC0415
