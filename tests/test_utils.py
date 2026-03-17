from unittest.mock import MagicMock, patch

from django.test import TestCase

from planet.utils import fetch_post_content, normalize_language, parse_feed


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
