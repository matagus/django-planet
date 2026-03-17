from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from planet.models import Author, Feed, Post, PostAuthorData
from tests.factories import FeedFactory, PostFactory


class CreateAuthorsForPostTest(TestCase):
    def test_creates_author_and_link(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "Jane Doe"}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 1)
        self.assertTrue(Author.objects.filter(name="Jane Doe").exists())

    def test_skips_missing_name_key(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"email": "x@example.com"}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_skips_empty_name(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "   "}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_handles_empty_authors_list(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_deduplicates_authors_via_get_or_create(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "Alice"}, {"name": "Alice"}])
        self.assertEqual(Author.objects.filter(name="Alice").count(), 1)


class FeedModelDeadCodeRemovedTest(TestCase):
    def test_no_should_update_method(self):
        self.assertFalse(hasattr(Feed, "should_update"))

    def test_no_retrieve_and_update_method(self):
        self.assertFalse(hasattr(Feed, "retrieve_and_update"))


def _make_feed_data(title="Real Feed Title", link="https://example.com"):
    feed_data = MagicMock()
    feed_data.href = "https://example.com/feed.xml"
    feed_data.status = 200
    feed_data.bozo = False
    feed_data.entries = []
    feed_data.feed = {
        "title": title,
        "link": link,
        "subtitle": "A subtitle",
        "language": "en",
    }
    feed_data.get = lambda key, default=None: {"etag": None, "updated_parsed": None}.get(key, default)
    return feed_data


class UpdateAllFeedsMetadataTest(TestCase):
    def test_stub_feed_gets_metadata_updated(self):
        """A stub feed (last_checked=None) should have title updated on first run."""
        feed = FeedFactory(title="example.com", last_checked=None)
        feed_data = _make_feed_data(title="Real Feed Title")

        with patch("planet.management.commands.planet_update_all_feeds.parse_feed", return_value=feed_data):
            call_command("planet_update_all_feeds")

        feed.refresh_from_db()
        self.assertEqual(feed.title, "Real Feed Title")

    def test_existing_feed_title_not_overwritten(self):
        """A feed with last_checked set should NOT have its title overwritten."""
        feed = FeedFactory(title="Existing Title", last_checked=timezone.now())
        feed_data = _make_feed_data(title="New Title From Feed")

        with patch("planet.management.commands.planet_update_all_feeds.parse_feed", return_value=feed_data):
            call_command("planet_update_all_feeds")

        feed.refresh_from_db()
        self.assertEqual(feed.title, "Existing Title")
