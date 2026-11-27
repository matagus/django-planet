from planet.models import Blog, Feed

from .base import AdminTestCase
from .factories import AuthorFactory, FeedFactory, PostAuthorDataFactory, PostFactory


class FeedAdminAddViewTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.add_url = self.admin_url("feed", "add")

    def test_add_page_shows_only_url_field(self):
        response = self.assertPageOk(self.add_url)
        self.assertIn(b'name="url"', response.content)
        self.assertNotIn(b'name="title"', response.content)

    def test_post_valid_url_creates_feed_and_blog(self):
        response = self.client.post(self.add_url, {"url": "https://example.com/feed.xml"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Blog.objects.count(), 1)
        feed = Feed.objects.get()
        self.assertEqual(feed.url, "https://example.com/feed.xml")
        self.assertEqual(feed.title, "example.com")
        self.assertEqual(feed.blog.title, "example.com")

    def test_post_duplicate_url_shows_validation_error(self):
        FeedFactory(url="https://example.com/feed.xml")
        response = self.client.post(self.add_url, {"url": "https://example.com/feed.xml"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A feed with this URL already exists", response.content)
        self.assertEqual(Feed.objects.count(), 1)

    def test_post_invalid_url_shows_validation_error(self):
        response = self.client.post(self.add_url, {"url": "not-a-url"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feed.objects.count(), 0)

    def test_change_page_shows_full_fieldsets(self):
        feed = FeedFactory()
        response = self.assertAdminPageOk("feed", "change", feed.pk)
        self.assertIn(b'name="title"', response.content)
        self.assertIn(b'name="url"', response.content)


class FeedAdminAuthorsListTest(AdminTestCase):
    def assertFeedChangeContains(self, feed, needle):
        response = self.assertAdminPageOk("feed", "change", feed.pk)
        self.assertIn(needle, response.content)
        return response

    def test_authors_list_shows_author_links(self):
        author = AuthorFactory(name="Ada Lovelace")
        post = PostFactory(authors=[author])
        self.assertFeedChangeContains(post.feed, b"Ada Lovelace")

    def test_authors_list_shows_no_authors_message(self):
        self.assertFeedChangeContains(FeedFactory(), b"No authors")


class AuthorAdminFeedsListTest(AdminTestCase):
    def test_feeds_list_shows_feed_links(self):
        author = AuthorFactory()
        post = PostFactory(authors=[author])
        response = self.assertAdminPageOk("author", "change", author.pk)
        self.assertIn(post.feed.title.encode(), response.content)

    def test_feeds_list_shows_no_feeds_message(self):
        author = AuthorFactory()
        response = self.assertAdminPageOk("author", "change", author.pk)
        self.assertIn(b"No feeds", response.content)


class HasPostsFilterTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.list_url = self.admin_url("feed", "changelist")

    def assertFilteredToSingleFeed(self, value, expected_feed):
        """Apply the has_posts filter and assert exactly one feed is listed."""
        response = self.assertPageOk(self.list_url, {"has_posts": value})
        self.assertContains(response, expected_feed.title)
        self.assertEqual(response.context["cl"].queryset.count(), 1)
        return response

    def test_filter_yes_returns_feeds_with_posts(self):
        feed_with_post = FeedFactory()
        PostFactory(feed=feed_with_post)
        FeedFactory()  # feed without posts
        self.assertFilteredToSingleFeed("yes", feed_with_post)

    def test_filter_no_returns_feeds_without_posts(self):
        feed_without_post = FeedFactory()
        PostFactory(feed=FeedFactory())  # a second feed that does have a post
        self.assertFilteredToSingleFeed("no", feed_without_post)


class FeedInlineReadOnlyTest(AdminTestCase):
    def blog_change_for(self, feed):
        """GET the admin change page for the blog owning ``feed``."""
        return self.assertAdminPageOk("blog", "change", feed.blog.pk)

    def test_feed_link_renders_in_blog_change_page(self):
        feed = FeedFactory()
        response = self.blog_change_for(feed)
        self.assertContains(response, self.admin_url("feed", "change", feed.pk))
        self.assertContains(response, feed.title)

    def test_inline_has_no_add_form(self):
        # has_add_permission returns False, so no empty add row should appear
        self.assertNotContains(self.blog_change_for(FeedFactory()), 'id="planet_feed-empty"')


class BlogAdminChangelistTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.list_url = self.admin_url("blog", "changelist")

    def test_changelist_loads(self):
        FeedFactory(language="en", is_active=True)
        FeedFactory(language="es", is_active=False)
        self.assertPageOk(self.list_url)

    def test_changelist_filter_by_language(self):
        feed_en = FeedFactory(language="en")
        FeedFactory(language="es")
        response = self.assertPageOk(self.list_url, {"feed__language": "en"})
        self.assertContains(response, feed_en.blog.title)


class PostAuthorDataAdminTest(AdminTestCase):
    def test_list_displays_author_name(self):
        author = AuthorFactory(name="Grace Hopper")
        PostAuthorDataFactory(author=author)
        response = self.assertAdminPageOk("postauthordata", "changelist")
        self.assertIn(b"Grace Hopper", response.content)
