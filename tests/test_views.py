from .base import PlanetTestCase
from .factories import AuthorFactory, BlogFactory, FeedFactory, FeedWithPostsFactory, PostFactory


class BlogViewsTest(PlanetTestCase):
    def setUp(self):
        self.blog = BlogFactory.create(title="Blog-1")
        self.feed = FeedFactory.create(title="Feed-1", blog=self.blog)

    def test_list(self):
        self.assertPageOk("/blogs/")

    def test_detail(self):
        self.assertSlugUrlWorks(self.blog)


class FeedViewsTest(PlanetTestCase):
    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post = PostFactory.create(feed=self.feed)

    def test_list(self):
        self.assertPageOk("/feeds/")

    def test_detail(self):
        self.assertSlugUrlWorks(self.feed)


class PostViewsTest(PlanetTestCase):
    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post = PostFactory.create(title="Post-1", feed=self.feed)

    def test_list(self):
        self.assertPageOk("/posts/")

    def test_detail(self):
        self.assertSlugUrlWorks(self.post)


class AuthorViewsTest(PlanetTestCase):
    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.author = AuthorFactory.create(name="Author-1")
        self.post_list = PostFactory.create_batch(size=3, feed=self.feed, authors=[self.author])

    def test_list(self):
        self.assertPageOk("/authors/")

    def test_detail(self):
        self.assertSlugUrlWorks(self.author)


class IndexViewTest(PlanetTestCase):
    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post = PostFactory.create(feed=self.feed)

    def test_index(self):
        self.assertPageOk("/")


class SearchViewTest(PlanetTestCase):
    def setUp(self):
        self.feed = FeedWithPostsFactory(posts__size=5)
        self.post_list = list(self.feed.post_set.all())

    def test_invalid_search(self):
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 302)

    def test_post_search(self):
        self.assertPageOk("/search/?search=go&q=post&w=posts")

    def test_author_search(self):
        self.assertPageOk("/search/?search=go&q=author&w=authors")

    def test_feed_search(self):
        self.assertPageOk("/search/?search=go&q=feed&w=feeds")

    def test_navbar_form_preserves_query_and_selection_after_search(self):
        response = self.assertPageOk("/search/?q=Adam&w=authors")
        self.assertContains(response, 'value="Adam"')
        self.assertContains(response, '<option value="authors" selected>')

    def test_navbar_form_is_empty_on_non_search_page(self):
        response = self.assertPageOk("/posts/")
        self.assertContains(response, 'name="q" value=""')
        self.assertNotContains(response, "selected>")
