from django.conf import settings
from django.core.checks import Tags, run_checks
from django.test import SimpleTestCase


def findings():
    return {item.id: item for item in run_checks(tags=[Tags.compatibility]) if item.id.startswith("planet.")}


class PlanetConfigurationChecksTest(SimpleTestCase):
    def test_working_configuration_has_no_diagnostics(self):
        self.assertEqual(findings(), {})

    def test_missing_pagination_is_an_error(self):
        with self.settings(INSTALLED_APPS=[app for app in settings.INSTALLED_APPS if app != "pagination"]):
            item = findings()["planet.E001"]
            self.assertTrue(item.is_serious())
            self.assertIn("INSTALLED_APPS", item.hint)

    def test_pagination_order_depends_on_app_template_discovery(self):
        apps = ["pagination", *(app for app in settings.INSTALLED_APPS if app != "pagination")]
        with self.settings(INSTALLED_APPS=apps):
            self.assertFalse(findings()["planet.W001"].is_serious())
            templates = [{**item, "APP_DIRS": False} for item in settings.TEMPLATES]
            with self.settings(TEMPLATES=templates):
                self.assertNotIn("planet.W001", findings())

    def test_middleware_and_standard_template_context(self):
        templates = [
            {"BACKEND": "django.template.backends.django.DjangoTemplates", "OPTIONS": {}},
            {
                "BACKEND": "django.template.backends.jinja2.Jinja2",
                "OPTIONS": {"context_processors": ["planet.context_processors.context"]},
            },
        ]
        with self.settings(MIDDLEWARE=[], TEMPLATES=templates):
            self.assertEqual(set(findings()), {"planet.W002", "planet.W003"})

    def test_missing_site_id_or_sites_app(self):
        with self.settings(SITE_ID=None):
            self.assertIn("planet.W004", findings())
        with self.settings(INSTALLED_APPS=[app for app in settings.INSTALLED_APPS if app != "django.contrib.sites"]):
            self.assertIn("planet.W004", findings())
