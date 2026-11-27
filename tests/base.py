"""Shared test scaffolding for the django-planet suite.

Keep common arrange/assert shapes here so individual tests state only what is
unique about them. Two rules govern this module:

1. Do not write ``tearDown`` in these tests. ``TestCase`` wraps every test in a
   transaction that is rolled back, so explicit deletes are dead code.
2. Build detail URLs from ``obj.get_absolute_url()`` instead of hardcoding
   slugs. Models derive slugs with ``slugify(title)``, and a literal slug will
   silently drift out of sync with the factory's title.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PlanetTestCase(TestCase):
    """Base class with helpers for planet views.

    Objects created in ``setUp`` are per-test, so tests may mutate them freely.
    Use ``setUpTestData`` on a subclass only for objects nothing mutates: those
    are shared across tests within the class and changes leak between them.
    """

    # ------------------------------------------------------------------ URLs

    def detail_url(self, obj):
        """Canonical detail URL for ``obj`` (includes the slug)."""
        return obj.get_absolute_url()

    def pk_only_url(self, obj):
        """Detail URL without the slug, which should redirect to the canonical one."""
        return obj.get_absolute_url().rsplit("/", 2)[0] + "/"

    # ----------------------------------------------------------- assertions

    def assertPageOk(self, url, data=None, *, client=None):
        """GET ``url`` and assert HTTP 200. Returns the response for further asserts."""
        response = (client or self.client).get(url, data)
        self.assertEqual(response.status_code, 200, f"Expected 200 from GET {url}")
        return response

    def assertRedirectToDetail(self, obj, *, client=None):
        """The PK-only URL must redirect (301) to the canonical slug URL."""
        response = (client or self.client).get(self.pk_only_url(obj))
        self.assertEqual(response.status_code, 301, f"Expected 301 from GET {self.pk_only_url(obj)}")
        return response

    def assertNotFound(self, url, *, client=None):
        response = (client or self.client).get(url)
        self.assertEqual(response.status_code, 404, f"Expected 404 from GET {url}")
        return response

    def assertSlugUrlWorks(self, obj, *, wrong_slug="other"):
        """Assert the full detail contract for one object: 301 then 200 then 404.

        Covers the three cases every planet detail view shares: missing slug
        redirects, correct slug renders, and a mismatched slug 404s.
        """
        self.assertRedirectToDetail(obj)
        self.assertPageOk(self.detail_url(obj))
        pk_part = self.detail_url(obj).rsplit("/", 2)
        self.assertNotFound(f"{pk_part[0]}/{obj.pk}/{wrong_slug}/")


class AdminTestCase(PlanetTestCase):
    """Logs in a superuser once per test; use for any admin view test."""

    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="password",
            email="admin@example.com",
        )
        self.client.force_login(self.superuser)

    def admin_url(self, model_name, action, *args):
        """URL for an admin view, e.g. ``admin_url("feed", "changelist")``."""
        return reverse(f"admin:planet_{model_name}_{action}", args=args)

    def assertAdminPageOk(self, model_name, action, *args, data=None):
        """GET an admin page and assert HTTP 200. Returns the response."""
        return self.assertPageOk(self.admin_url(model_name, action, *args), data)
