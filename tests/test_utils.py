from unittest.mock import MagicMock, patch

from django.template import Context, Template
from django.test import TestCase

from planet.models import Author, Blog, Feed, Post
from planet.utils import fetch_post_content, normalize_language, parse_feed
from .base import PlanetTestCase


class ParseFeedTest(TestCase):
    def _make_result(self):
        result = MagicMock()
        result.entries = []
        result.status = 200
        return result

    @patch("planet.utils.feedparser.parse")
    def test_no_etag_no_modified(self, mock_parse):
        mock_parse.return_value = self._make_result()
        parse_feed("https://example.com/feed.xml")
        _, kwargs = mock_parse.call_args
        self.assertNotIn("etag", kwargs)
        self.assertNotIn("modified", kwargs)

    @patch("planet.utils.feedparser.parse")
    def test_with_etag(self, mock_parse):
        mock_parse.return_value = self._make_result()
        parse_feed("https://example.com/feed.xml", etag="abc123")
        _, kwargs = mock_parse.call_args
        self.assertEqual(kwargs["etag"], "abc123")
        self.assertNotIn("modified", kwargs)

    @patch("planet.utils.feedparser.parse")
    def test_with_modified_only(self, mock_parse):
        mock_parse.return_value = self._make_result()
        parse_feed("https://example.com/feed.xml", modified="Mon, 01 Jan 2024 00:00:00 GMT")
        _, kwargs = mock_parse.call_args
        self.assertEqual(kwargs["modified"], "Mon, 01 Jan 2024 00:00:00 GMT")
        self.assertNotIn("etag", kwargs)

    @patch("planet.utils.feedparser.parse")
    def test_returns_parsed_result(self, mock_parse):
        result = self._make_result()
        mock_parse.return_value = result
        self.assertIs(parse_feed("https://example.com/feed.xml"), result)


class FetchPostContentTest(TestCase):
    @patch("planet.utils.urllib.request.urlopen")
    @patch("planet.utils.urllib.request.Request")
    def test_success_returns_summary(self, mock_request, mock_urlopen):
        html = b"<html><body><p>Hello world</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fetch_post_content("https://example.com/post")
        self.assertIsNotNone(result)

    @patch("planet.utils.urllib.request.urlopen", side_effect=OSError("timeout"))
    @patch("planet.utils.urllib.request.Request")
    def test_exception_returns_none(self, mock_request, mock_urlopen):
        result = fetch_post_content("https://example.com/post")
        self.assertIsNone(result)


class NormalizeLanguageTest(TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(normalize_language(None))

    def test_locale_stripped_to_language(self):
        self.assertEqual(normalize_language("en-US"), "en")

    def test_plain_language_unchanged(self):
        self.assertEqual(normalize_language("es"), "es")


class SidebarLabelTest(PlanetTestCase):
    """Sidebar labels are a template concern, not a model property.

    planet/blocks/nav_list.html resolves `label_field` through the `attr` tag, so
    a downstream project can relabel the sidebar by overriding the inclusion tag
    or template without subclassing models or adding UI fields to them.
    """

    def test_models_expose_no_sidebar_label(self):
        for model in (Blog, Feed, Post, Author):
            self.assertFalse(hasattr(model, "sidebar_label"), f"{model.__name__} leaked UI field")

    def test_attr_tag_prefers_first_non_empty_candidate(self):
        obj = type("X", (), {"display_name": "", "title": "T", "name": "N"})()
        out = Template('{% load planet_tags %}{% attr obj "display_name,title,name" %}').render(Context({"obj": obj}))
        self.assertEqual(out.strip(), "T")

    def test_attr_tag_resolves_methods_without_args(self):
        obj = type("X", (), {"get_absolute_url": lambda self: "/x/"})()
        out = Template('{% load planet_tags %}{% attr obj "get_absolute_url" %}').render(Context({"obj": obj}))
        self.assertEqual(out.strip(), "/x/")

    def test_attr_tag_missing_field_is_blank_not_error(self):
        out = Template('{% load planet_tags %}{% attr obj "nope,also_missing" %}').render(Context({"obj": object()}))
        self.assertEqual(out.strip(), "")

    def test_custom_label_field_needs_only_a_template_override(self):
        item = type("X", (), {"nickname": "Nick", "title": "", "get_absolute_url": "/x/"})()
        out = Template(
            '{% load planet_tags %}{% include "planet/blocks/nav_list.html" '
            'with items=items title="T" label_field="nickname,title" %}'
        ).render(Context({"items": [item]}))
        self.assertIn("Nick", out)
        self.assertNotIn(">\n        \n    </a>", out)  # no blank anchor text

    def test_escaping_applies_to_resolved_labels(self):
        item = type("X", (), {"title": "<script>x</script>", "get_absolute_url": "/x/"})()
        out = Template(
            '{% load planet_tags %}{% include "planet/blocks/nav_list.html" '
            'with items=items title="T" label_field="title" %}'
        ).render(Context({"items": [item]}))
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)
