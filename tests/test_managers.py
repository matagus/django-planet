from django.template import Context, Template
from django.test import TestCase

from .base import PlanetTestCase
from .factories import AuthorFactory, BlogFactory, FeedFactory, PostFactory
from .mocks import _make_entry_data, _make_feed_data
from planet.models import Author, Blog, Feed, Post
from planet.utils import md5_hash


class FeedGuidConsistencyTestCase(PlanetTestCase):
    """Regression tests: get_by_url() must find feeds created via create_from()."""

    def setUp(self):
        self.url = "https://fly.io/django-beats/feed.xml"
        self.blog = BlogFactory.create()
        # feed['id'] deliberately differs from the URL: guid must come from the URL.
        self.feed_data = _make_feed_data(href=self.url, link=self.url, feed_id="urn:something:different")

    def test_create_from_guid_uses_url_not_feed_id(self):
        """FeedQuerySet.create_from() guid must equal md5(url), ignoring feed['id']."""
        feed = Feed.objects.create_from(self.feed_data, self.blog)

        self.assertEqual(feed.guid, md5_hash(self.url))
        self.assertNotEqual(feed.guid, md5_hash("urn:something:different"))

    def test_get_by_url_finds_feed_created_by_create_from(self):
        """Feed.objects.get_by_url(url) must find a feed created by create_from() even when feed['id'] differs."""
        created = Feed.objects.create_from(self.feed_data, self.blog)
        found = Feed.objects.get_by_url(self.url)

        self.assertEqual(found.pk, created.pk)


class ManagersTestCase(TestCase):
    def setUp(self):
        self.author1 = AuthorFactory.create()
        self.author2 = AuthorFactory.create()

        self.another_posts = PostFactory.create_batch(size=3, feed=FeedFactory.create(), authors=[self.author1])
        self.site_posts = PostFactory.create_batch(size=5, feed=FeedFactory.create(), authors=[self.author2])

    def test_posts(self):
        self.assertEqual(Post.objects.count(), 8)

        site_posts_qs = Post.objects.all()
        for post in self.site_posts:
            self.assertTrue(post in site_posts_qs)

    def test_feeds(self):
        self.assertEqual(Feed.objects.count(), 2)
        self.assertTrue(self.site_posts[0].feed in Feed.objects.all())

    def test_blogs(self):
        self.assertEqual(Blog.objects.count(), 2)
        self.assertTrue(self.site_posts[0].feed.blog in Blog.objects.all())

    def test_author_count(self):
        self.assertEqual(Author.objects.count(), 2)

    def test_author_posts_counts(self):
        self.assertEqual(Post.objects.filter(authors=self.author1).count(), 3)


class AuthorForFeedTest(PlanetTestCase):
    """AuthorQuerySet.for_feed() backs the {% authors_for_feed %} inclusion tag.

    Regression: commit 6005ddc moved manager methods onto QuerySets and dropped
    PostManager.for_feed(), but AuthorQuerySet never defined its own, so the tag
    raised AttributeError. Nothing called it in the shipped templates, so no test
    caught it.
    """

    def setUp(self):
        self.feed = FeedFactory()
        self.author = AuthorFactory(name="In Feed")
        PostFactory(feed=self.feed, authors=[self.author])

        self.other_feed = FeedFactory()
        self.other_author = AuthorFactory(name="Elsewhere")
        PostFactory(feed=self.other_feed, authors=[self.other_author])

    def test_returns_only_authors_of_that_feed(self):
        authors = list(Author.objects.for_feed(self.feed))
        self.assertEqual(authors, [self.author])

    def test_deduplicates_authors_with_several_posts(self):
        PostFactory(feed=self.feed, authors=[self.author])
        self.assertEqual(Author.objects.for_feed(self.feed).count(), 1)

    def test_inclusion_tag_renders_author_names(self):
        out = Template("{% load planet_tags %}{% authors_for_feed feed %}").render(Context({"feed": self.feed}))
        self.assertIn("Authors for this feed", out)
        self.assertIn("In Feed", out)
        self.assertNotIn("Elsewhere", out)


class FeedparserDataExtractionTestCase(PlanetTestCase):
    """
    Test that managers properly extract and fall back data from feedparser objects.
    These tests verify fixes for missing titles, URLs, and author names.
    """

    def create_blog_from(self, **feed_data_kwargs):
        """Run get_or_create_from_feed() against mocked feed data; return (blog, created)."""
        return Blog.objects.get_or_create_from_feed(_make_feed_data(**feed_data_kwargs))

    def test_blog_get_or_create_missing_link_fallback_to_href(self):
        """BlogQuerySet.get_or_create_from_feed() should fall back to feed_data.href when feed.link is missing."""
        blog, created = self.create_blog_from(
            href="https://example.com/feed.xml",
            title="My Blog",
            link="",  # Missing link
        )

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://example.com/feed.xml")
        self.assertEqual(blog.title, "My Blog")

    def test_blog_get_or_create_missing_title_fallback_to_domain(self):
        """BlogQuerySet.get_or_create_from_feed() should fall back to URL domain when feed.title is missing."""
        blog, created = self.create_blog_from(
            href="https://foo.example.com/path/to/feed.xml",
            title="",  # Missing title
            link="https://foo.example.com",
        )

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://foo.example.com")
        self.assertEqual(blog.title, "foo.example.com")

    def test_blog_get_or_create_both_missing_uses_domain_from_href(self):
        """BlogQuerySet.get_or_create_from_feed() should extract domain from href when both link and title are missing."""
        blog, created = self.create_blog_from(
            href="https://blog.test.org/rss",
            title="",
            link="",
        )

        self.assertTrue(created)
        self.assertEqual(blog.url, "https://blog.test.org/rss")
        self.assertEqual(blog.title, "blog.test.org")

    def test_feed_create_from_missing_title_fallback_to_domain(self):
        """FeedQuerySet.create_from() should fall back to URL domain when feed.title is missing."""
        blog = BlogFactory.create()
        feed_data = _make_feed_data(
            href="https://example.org/feed",
            title="",  # Missing title
        )

        feed = Feed.objects.create_from(feed_data, blog)

        self.assertEqual(feed.title, "example.org")
        self.assertEqual(feed.url, "https://example.org/feed")

    def test_feed_create_from_preserves_title_when_present(self):
        """FeedQuerySet.create_from() should preserve title when present."""
        blog = BlogFactory.create()
        feed_data = _make_feed_data(
            href="https://example.org/feed",
            title="My Feed Title",
        )

        feed = Feed.objects.create_from(feed_data, blog)

        self.assertEqual(feed.title, "My Feed Title")

    # ------------------------------------------------------------- posts

    def create_post(self, **entry_kwargs):
        """Post.objects.create_from() against an entry built from ``entry_kwargs``."""
        feed = FeedFactory.create()
        return Post.objects.create_from(_make_entry_data(**entry_kwargs), feed)

    def create_post_with_authors(self, **entry_kwargs):
        """Post.objects.create_with_authors() against an entry built from ``entry_kwargs``."""
        feed = FeedFactory.create()
        return Post.objects.create_with_authors(_make_entry_data(**entry_kwargs), feed)

    def test_post_create_from_missing_link_returns_none(self):
        """PostQuerySet.create_from() should return None and not create post when entry.link is missing."""
        result = self.create_post(link="", title="Entry Title")

        self.assertIsNone(result)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_create_from_missing_title_sets_empty_string(self):
        """PostQuerySet.create_from() should set post.title to empty string when entry.title is missing."""
        post = self.create_post(link="https://example.com/post1", title="")

        self.assertIsNotNone(post)
        self.assertEqual(post.title, "")
        self.assertEqual(post.url, "https://example.com/post1")

    def test_post_create_with_authors_fallback_to_entry_author_string(self):
        """PostQuerySet.create_with_authors() should create author from entry.author string when entry.authors is empty."""
        post = self.create_post_with_authors(
            link="https://example.com/post1",
            title="Post Title",
            authors=[],  # Empty authors list
            author="John Doe",  # But simple author string is provided
        )

        self.assertIsNotNone(post)
        # Author should have been created from the simple author string
        authors = Author.objects.filter(name="John Doe")
        self.assertEqual(authors.count(), 1)
        self.assertIn(authors.first(), post.authors.all())

    def test_post_create_with_authors_ignores_empty_author_string(self):
        """PostQuerySet.create_with_authors() should ignore entry.author if it's empty or whitespace."""
        post = self.create_post_with_authors(
            link="https://example.com/post1",
            title="Post Title",
            authors=[],
            author="   ",  # Whitespace only
        )

        self.assertIsNotNone(post)
        self.assertEqual(post.authors.count(), 0)

    def test_post_create_with_authors_returns_none_for_missing_url(self):
        """PostQuerySet.create_with_authors() should return None when entry has no URL."""
        result = self.create_post_with_authors(
            link="",  # Missing link
            title="Post Title",
            authors=[],
            author="John Doe",
        )

        self.assertIsNone(result)
        self.assertEqual(Post.objects.count(), 0)
        # Author should not have been created if the post was not created
        self.assertEqual(Author.objects.count(), 0)

    def test_author_deduplication_multiple_posts_same_author(self):
        """Multiple posts with the same author should create only one Author record."""
        feed = FeedFactory.create()

        # Create 5 posts with the same author name
        for i in range(5):
            entry_data = _make_entry_data(
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
            entry_data = _make_entry_data(
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


class StubCreationTestCase(PlanetTestCase):
    """Stub blog/feed creation derives its title from the URL hostname."""

    URL = "https://example.com/feed.xml"

    def make_stub_feed(self, url=URL):
        """Create the stub blog + stub feed pair for ``url`` and return the feed."""
        blog, _ = Blog.objects.get_or_create_stub(url)
        return Feed.objects.create_stub(url, blog)

    def test_blog_get_or_create_stub_uses_hostname_as_title(self):
        blog, created = Blog.objects.get_or_create_stub(self.URL)
        self.assertTrue(created)
        self.assertEqual(blog.title, "example.com")
        self.assertEqual(blog.url, self.URL)

    def test_blog_get_or_create_stub_is_idempotent(self):
        Blog.objects.get_or_create_stub(self.URL)
        _, created = Blog.objects.get_or_create_stub(self.URL)
        self.assertFalse(created)
        self.assertEqual(Blog.objects.count(), 1)

    def test_feed_create_stub_uses_hostname_as_title(self):
        feed = self.make_stub_feed()
        self.assertEqual(feed.title, "example.com")
        self.assertEqual(feed.url, self.URL)
        self.assertEqual(feed.blog.url, self.URL)
        self.assertIsNone(feed.last_checked)

    def test_feed_create_stub_guid_is_md5_of_url(self):
        self.assertEqual(self.make_stub_feed().guid, md5_hash(self.URL))

    def test_feed_get_by_url_works_after_create_stub(self):
        self.make_stub_feed()
        self.assertEqual(Feed.objects.get_by_url(self.URL).url, self.URL)


class PostDuplicateSkipTestCase(PlanetTestCase):
    """create_from() must skip a post whose URL already exists in another feed."""

    URL = "https://example.com/some-post"

    def setUp(self):
        self.existing_feed = FeedFactory()
        PostFactory(feed=self.existing_feed, url=self.URL, guid=md5_hash(self.URL))
        self.other_feed = FeedFactory()

    def attempt_duplicate_creation(self):
        """Try to import self.URL into a second feed; returns the created post or None."""
        return Post.objects.create_from(_make_entry_data(link=self.URL, title="Some Post"), self.other_feed)

    def test_create_from_skips_post_when_url_exists_in_another_feed(self):
        """PostQuerySet.create_from() returns None when a post with the same URL already exists in a different feed."""
        self.assertIsNone(self.attempt_duplicate_creation())

    def test_create_from_does_not_save_on_duplicate(self):
        """PostQuerySet.create_from() does not create a new Post row when the URL is a duplicate."""
        self.attempt_duplicate_creation()
        self.assertEqual(Post.objects.count(), 1)
