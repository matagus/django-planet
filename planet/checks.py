"""Check installation settings without accessing the database."""

from django.apps import apps
from django.conf import settings
from django.core.checks import Error, Tags, Warning, register


@register(Tags.compatibility)
def check_planet_configuration(app_configs, **kwargs):
    if app_configs is not None and all(config.name != "planet" for config in app_configs):
        return []

    installed = [config.name for config in apps.get_app_configs()]
    if "planet" not in installed:
        return []

    templates = [
        item for item in settings.TEMPLATES if item.get("BACKEND") == "django.template.backends.django.DjangoTemplates"
    ]
    messages = []
    if "pagination" not in installed:
        messages.append(
            Error(
                "django-planet requires the pagination app.",
                hint="Add 'pagination' after 'planet' in INSTALLED_APPS.",
                id="planet.E001",
            )
        )
    elif installed.index("pagination") < installed.index("planet") and any(
        template.get("APP_DIRS") for template in templates
    ):
        messages.append(
            Warning(
                "The pagination app precedes planet in template discovery order.",
                hint="List 'planet' before 'pagination' in INSTALLED_APPS to use Planet's pagination template.",
                id="planet.W001",
            )
        )

    if "pagination.middleware.PaginationMiddleware" not in settings.MIDDLEWARE:
        messages.append(
            Warning(
                "Planet pagination middleware is not configured.",
                hint="Add 'pagination.middleware.PaginationMiddleware' to MIDDLEWARE.",
                id="planet.W002",
            )
        )
    if not any(
        "planet.context_processors.context" in template.get("OPTIONS", {}).get("context_processors", [])
        for template in templates
    ):
        messages.append(
            Warning(
                "The Planet context processor is not configured.",
                hint="Add 'planet.context_processors.context' to the Django backend's OPTIONS['context_processors'].",
                id="planet.W003",
            )
        )
    if "django.contrib.sites" not in installed or not getattr(settings, "SITE_ID", None):
        messages.append(
            Warning(
                "The default Planet site is not configured.",
                hint="Add 'django.contrib.sites' to INSTALLED_APPS and set SITE_ID to your site's ID.",
                id="planet.W004",
            )
        )
    return messages
