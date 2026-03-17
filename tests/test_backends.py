from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from planet.backends import get_post_filter_backend
from planet.backends.accept_all import AcceptAllBackend
from planet.backends.keyword import KeywordFilterBackend


def make_entry(title="", summary=""):
    return SimpleNamespace(title=title, summary=summary, link="http://example.com/post")


class AcceptAllBackendTest(TestCase):
    def setUp(self):
        self.backend = AcceptAllBackend()
        self.feed = SimpleNamespace(url="http://example.com/feed")

    def test_returns_all_entries(self):
        entries = [make_entry("Entry 1"), make_entry("Entry 2")]
        result = self.backend.filter_entries(entries, self.feed)
        self.assertEqual(result, entries)

    def test_returns_a_list(self):
        entries = (make_entry("Entry") for _ in range(3))  # generator
        result = self.backend.filter_entries(entries, self.feed)
        self.assertIsInstance(result, list)

    def test_empty_entries(self):
        result = self.backend.filter_entries([], self.feed)
        self.assertEqual(result, [])


class KeywordFilterBackendTest(TestCase):
    def setUp(self):
        self.feed = SimpleNamespace(url="http://example.com/feed")

    def _make_backend(self, keywords):
        with patch.dict("planet.settings.PLANET_CONFIG", {"TOPIC_KEYWORDS": keywords}):
            return KeywordFilterBackend()

    def test_keyword_in_title_accepted(self):
        backend = self._make_backend(["python"])
        entries = [make_entry(title="Python is great")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(result, entries)

    def test_keyword_in_summary_accepted(self):
        backend = self._make_backend(["django"])
        entries = [make_entry(title="A post", summary="This is about Django web framework")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(result, entries)

    def test_no_keyword_match_rejected(self):
        backend = self._make_backend(["python"])
        entries = [make_entry(title="JavaScript news", summary="All about JS")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(result, [])

    def test_case_insensitive(self):
        backend = self._make_backend(["PYTHON"])
        entries = [make_entry(title="python rocks")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(result, entries)

    def test_empty_keywords_accepts_all(self):
        backend = self._make_backend([])
        entries = [make_entry("Anything"), make_entry("Something else")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(result, entries)

    def test_info_log_on_rejection(self):
        backend = self._make_backend(["python"])
        entries = [make_entry(title="JavaScript news")]
        with self.assertLogs("planet.backends.keyword", level="INFO") as cm:
            backend.filter_entries(entries, self.feed)
        self.assertTrue(any("Rejected" in line for line in cm.output))

    def test_mixed_entries(self):
        backend = self._make_backend(["python"])
        entries = [make_entry(title="Python post"), make_entry(title="Java post")]
        result = backend.filter_entries(entries, self.feed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Python post")


class GetPostFilterBackendTest(TestCase):
    def test_loads_default_accept_all(self):
        backend = get_post_filter_backend()
        self.assertIsInstance(backend, AcceptAllBackend)

    def test_loads_custom_backend_via_patch(self):
        with patch.dict(
            "planet.settings.PLANET_CONFIG",
            {"POST_FILTER_BACKEND": "planet.backends.keyword.KeywordFilterBackend", "TOPIC_KEYWORDS": []},
        ):
            backend = get_post_filter_backend()
        self.assertIsInstance(backend, KeywordFilterBackend)

    def test_raises_on_invalid_path(self):
        with patch.dict("planet.settings.PLANET_CONFIG", {"POST_FILTER_BACKEND": "planet.backends.nonexistent.Foo"}):
            with self.assertRaises(ImportError):
                get_post_filter_backend()
