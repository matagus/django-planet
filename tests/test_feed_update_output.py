from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from tests.factories import FeedFactory
from tests.mocks import _make_feed_data

COMMAND = "planet_update_all_feeds"
COMMAND_MODULE = f"planet.management.commands.{COMMAND}"


class FeedUpdateOutputTest(TestCase):
    def test_summary_shown_at_default_verbosity_without_logging(self):
        stdout, stderr = StringIO(), StringIO()
        call_command(COMMAND, stdout=stdout, stderr=stderr, no_color=True)
        self.assertIn("0 feeds checked, 0 new posts, 0 errors", stdout.getvalue())
        self.assertNotIn("Starting feed update", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_verbose_output_reports_not_modified_without_printing_the_feed_url(self):
        feed = FeedFactory(url="https://example.com/test-feed")
        data = _make_feed_data()
        data.status = 304
        stdout, stderr = StringIO(), StringIO()
        with patch(f"{COMMAND_MODULE}.parse_feed", return_value=data):
            call_command(COMMAND, verbosity=2, stdout=stdout, stderr=stderr, no_color=True)

        self.assertIn("Starting feed update: 1 active feeds", stdout.getvalue())
        self.assertIn(f"Feed #{feed.pk} not modified (304)", stdout.getvalue())
        self.assertIn("1 feeds checked, 0 new posts, 0 errors", stdout.getvalue())
        self.assertNotIn(feed.url, stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_quiet_output_still_reports_each_failed_feed_and_checks_the_other_feeds(self):
        unreachable = FeedFactory()
        malformed = FeedFactory()
        unchanged = FeedFactory()
        invalid = _make_feed_data()
        invalid.bozo = True
        invalid.bozo_exception = ValueError("invalid test feed")
        data = _make_feed_data()
        data.status = 304
        stdout, stderr = StringIO(), StringIO()

        def resolve(url, **kwargs):
            if url == unreachable.url:
                raise OSError("unreachable test feed")
            return invalid if url == malformed.url else data

        with (
            patch(f"{COMMAND_MODULE}.parse_feed", side_effect=resolve),
            patch(f"{COMMAND_MODULE}.logger") as logger,
        ):
            call_command(COMMAND, verbosity=0, stdout=stdout, stderr=stderr, no_color=True)

        self.assertEqual(stdout.getvalue(), "")
        self.assertIn(f"Feed #{unreachable.pk}: fetch failed", stderr.getvalue())
        self.assertIn(f"Feed #{malformed.pk}: could not parse the empty feed", stderr.getvalue())
        self.assertNotIn("unreachable test feed", stderr.getvalue())
        self.assertNotIn("invalid test feed", stderr.getvalue())
        logger.error.assert_called_once()
        logger.warning.assert_called_once()
        unchanged.refresh_from_db()
        self.assertIsNotNone(unchanged.last_checked)
