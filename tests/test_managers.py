from unittest.mock import MagicMock, PropertyMock
from urllib.parse import urlparse

from django.test import TestCase

from .factories import AuthorFactory, BlogFactory, FeedFactory, PostFactory
from planet.models import Blog, Feed, Post, Author


class ManagersTestCase(TestCase):

    def setUp(self):
        self.author1 = AuthorFactory.create()
        self.author2 = AuthorFactory.create()

        self.another_feed = FeedFactory.create()
        self.another_posts = PostFactory.create_batch(size=3, feed=self.another_feed, authors=[self.author1])

        self.my_feed = FeedFactory.create()
        self.site_posts = PostFactory.create_batch(size=5, feed=self.my_feed, authors=[self.author2])

    def test_posts(self):
        self.assertEqual(Post.objects.count(), 8)

        site_posts_qs = Post.objects.all()
        for post in self.site_posts:
            self.assertTrue(post in site_posts_qs)

    def test_feeds(self):
        self.assertEqual(Feed.objects.count(), 2)
        self.assertTrue(self.my_feed in Feed.objects.all())

    def test_blogs(self):
        self.assertEqual(Blog.objects.count(), 2)
        self.assertTrue(self.my_feed.blog in Blog.objects.all())

    def test_author_count(self):
        self.assertEqual(Author.objects.count(), 2)

    def test_author_posts_counts(self):
        self.assertEqual(Post.objects.filter(authors=self.author1).count(), 3)


class FeedparserDataExtractionTestCase(TestCase):
    """
    Test that managers properly extract and fall back data from feedparser objects.
    These tests verify fixes for missing titles, URLs, and author names.
    """

    def _make_feed_data(self, href="https://example.com/feed.xml", title="", link=""):
        """Create a mock feedparser feed_data object."""
        feed_data = MagicMock()
        feed_data.href = href
        feed_data.feed = {
            "title": title,
            "link": link,
            "subtitle": "",
            "id": "feed-id",
            "language": "en",
        }
        feed_data.entries = []
        feed_data.get = lambda key, default=None: {
            "etag": None,
            "updated_parsed": None,
        }.get(key, default)
        return feed_data

    def _make_entry_data(self, link="", title="", authors=None, author=""):
        """Create a mock feedparser entry_data object."""
        if authors is None:
            authors = []

        class MockEntryData(dict):
            """A dict-like object that mimics feedparser entry data."""

            def get(self, key, default=""):
                data = {
                    "link": link,
                    "title": title,
                    "authors": authors,
                    "author": author,
                }
                return data.get(key, default)

            # Make published_parsed and summary_detail raise AttributeError
            @property
            def published_parsed(self):
                raise AttributeError("published_parsed")

            @property
            def summary_detail(self):
                raise AttributeError("summary_detail")

            @property
            def summary(self):
                return "Test summary"

        return MockEntryData()

    def test_blog_get_or_create_missing_link_fallback_to_href(self):
        """BlogManager.get_or_create_from_feed() should fall back to feed_data.href when feed.link is missing."""
        feed_data = self._make_feed_data(
            href="https://example.com/feed.xml",
            title="My Blog",
            link="",  # Missing link
        )

        blog, created = Blog.objects.get_or_create_from_feed(feed_data)

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://example.com/feed.xml")
        self.assertEqual(blog.title, "My Blog")

    def test_blog_get_or_create_missing_title_fallback_to_domain(self):
        """BlogManager.get_or_create_from_feed() should fall back to URL domain when feed.title is missing."""
        feed_data = self._make_feed_data(
            href="https://foo.example.com/path/to/feed.xml",
            title="",  # Missing title
            link="https://foo.example.com",
        )

        blog, created = Blog.objects.get_or_create_from_feed(feed_data)

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://foo.example.com")
        self.assertEqual(blog.title, "foo.example.com")

    def test_blog_get_or_create_both_missing_uses_domain_from_href(self):
        """BlogManager.get_or_create_from_feed() should extract domain from href when both link and title are missing."""
        feed_data = self._make_feed_data(
            href="https://blog.test.org/rss",
            title="",
            link="",
        )

        blog, created = Blog.objects.get_or_create_from_feed(feed_data)

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://blog.test.org/rss")
        self.assertEqual(blog.title, "blog.test.org")

    def test_feed_create_from_missing_title_fallback_to_domain(self):
        """FeedManager.create_from() should fall back to URL domain when feed.title is missing."""
        blog = BlogFactory.create()
        feed_data = self._make_feed_data(
            href="https://example.org/feed",
            title="",  # Missing title
        )

        feed = Feed.objects.create_from(feed_data, blog)

        self.assertEqual(feed.title, "example.org")
        self.assertEqual(feed.url, "https://example.org/feed")

    def test_feed_create_from_preserves_title_when_present(self):
        """FeedManager.create_from() should preserve title when present."""
        blog = BlogFactory.create()
        feed_data = self._make_feed_data(
            href="https://example.org/feed",
            title="My Feed Title",
        )

        feed = Feed.objects.create_from(feed_data, blog)

        self.assertEqual(feed.title, "My Feed Title")

    def test_post_create_from_missing_link_returns_none(self):
        """PostManager.create_from() should return None and not create post when entry.link is missing."""
        feed = FeedFactory.create()
        entry_data = self._make_entry_data(
            link="",  # Missing link
            title="Entry Title",
        )

        result = Post.objects.create_from(entry_data, feed)

        self.assertIsNone(result)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_create_from_missing_title_sets_empty_string(self):
        """PostManager.create_from() should set post.title to empty string when entry.title is missing."""
        feed = FeedFactory.create()
        entry_data = self._make_entry_data(
            link="https://example.com/post1",
            title="",  # Missing title
        )

        post = Post.objects.create_from(entry_data, feed)

        self.assertIsNotNone(post)
        self.assertEqual(post.title, "")
        self.assertEqual(post.url, "https://example.com/post1")

    def test_post_create_with_authors_fallback_to_entry_author_string(self):
        """PostManager.create_with_authors() should create author from entry.author string when entry.authors is empty."""
        feed = FeedFactory.create()
        entry_data = self._make_entry_data(
            link="https://example.com/post1",
            title="Post Title",
            authors=[],  # Empty authors list
            author="John Doe",  # But simple author string is provided
        )

        post = Post.objects.create_with_authors(entry_data, feed)

        self.assertIsNotNone(post)
        # Author should have been created from the simple author string
        authors = Author.objects.filter(name="John Doe")
        self.assertEqual(authors.count(), 1)
        self.assertIn(authors.first(), post.authors.all())

    def test_post_create_with_authors_ignores_empty_author_string(self):
        """PostManager.create_with_authors() should ignore entry.author if it's empty or whitespace."""
        feed = FeedFactory.create()
        entry_data = self._make_entry_data(
            link="https://example.com/post1",
            title="Post Title",
            authors=[],
            author="   ",  # Whitespace only
        )

        post = Post.objects.create_with_authors(entry_data, feed)

        self.assertIsNotNone(post)
        self.assertEqual(post.authors.count(), 0)

    def test_post_create_with_authors_returns_none_for_missing_url(self):
        """PostManager.create_with_authors() should return None when entry has no URL."""
        feed = FeedFactory.create()
        entry_data = self._make_entry_data(
            link="",  # Missing link
            title="Post Title",
            authors=[],
            author="John Doe",
        )

        result = Post.objects.create_with_authors(entry_data, feed)

        self.assertIsNone(result)
        self.assertEqual(Post.objects.count(), 0)
        # Author should not have been created if the post was not created
        self.assertEqual(Author.objects.count(), 0)

    def test_author_deduplication_multiple_posts_same_author(self):
        """Multiple posts with the same author should create only one Author record."""
        feed = FeedFactory.create()

        # Create 5 posts with the same author name
        for i in range(5):
            entry_data = self._make_entry_data(
                link=f"https://example.com/post{i}",
                title=f"Post {i}",
                authors=[],
                author="Jane Smith",
            )
            Post.objects.create_with_authors(entry_data, feed)

        # Should have only 1 Author record, not 5
        self.assertEqual(Author.objects.count(), 1)
        jane = Author.objects.get(name="Jane Smith")

        # All 5 posts should be linked to this one author
        self.assertEqual(jane.post_set.count(), 5)

    def test_author_deduplication_same_feed_different_authors(self):
        """Multiple posts with different authors should create separate Author records."""
        feed = FeedFactory.create()

        authors_to_create = ["Alice", "Bob", "Charlie"]

        for i, author_name in enumerate(authors_to_create):
            entry_data = self._make_entry_data(
                link=f"https://example.com/post{i}",
                title=f"Post by {author_name}",
                authors=[],
                author=author_name,
            )
            Post.objects.create_with_authors(entry_data, feed)

        # Should have 3 separate Author records
        self.assertEqual(Author.objects.count(), 3)

        # Each author should be linked to exactly one post
        for author_name in authors_to_create:
            author = Author.objects.get(name=author_name)
            self.assertEqual(author.post_set.count(), 1)
