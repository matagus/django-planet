from django.test import TestCase

from .factories import AuthorFactory, BlogFactory, FeedFactory, FeedWithPostsFactory, PostFactory


class BlogViewsTest(TestCase):
    def setUp(self):
        self.blog = BlogFactory(title="Blog-1")
        self.feed = FeedFactory(title="Feed-1", blog=self.blog)

    def test_list(self):
        response = self.client.get("/blogs/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        url = self.blog.get_absolute_url()
        response = self.client.get(url.rsplit("/", 2)[0] + "/")  # pk-only URL redirects to the canonical one
        self.assertRedirects(response, url, status_code=301)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/blogs/99999/wrong-slug/")  # nonexistent pk
        self.assertContains(response, "Not Found", status_code=404)


class FeedViewsTest(TestCase):
    def setUp(self):
        self.feed = FeedWithPostsFactory(title="Feed-1", posts__size=1)

    def test_list(self):
        response = self.client.get("/feeds/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        url = self.feed.get_absolute_url()
        response = self.client.get(url.rsplit("/", 2)[0] + "/")
        self.assertRedirects(response, url, status_code=301)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/feeds/99999/wrong-slug/")  # nonexistent pk
        self.assertContains(response, "Not Found", status_code=404)


class PostViewsTest(TestCase):
    def setUp(self):
        self.post = PostFactory(title="Post-1")

    def test_list(self):
        response = self.client.get("/posts/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        url = self.post.get_absolute_url()
        response = self.client.get(url.rsplit("/", 2)[0] + "/")
        self.assertRedirects(response, url, status_code=301)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/posts/99999/wrong-slug/")  # nonexistent pk
        self.assertContains(response, "Not Found", status_code=404)


class AuthorViewsTest(TestCase):
    def setUp(self):
        self.author = AuthorFactory(name="Author-1")
        self.feed = FeedWithPostsFactory(posts__authors=[self.author])

    def test_list(self):
        response = self.client.get("/authors/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        url = self.author.get_absolute_url()
        response = self.client.get(url.rsplit("/", 2)[0] + "/")
        self.assertRedirects(response, url, status_code=301)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/authors/99999/wrong-slug/")  # nonexistent pk
        self.assertContains(response, "Not Found", status_code=404)


class IndexViewTest(TestCase):
    def setUp(self):
        self.feed = FeedWithPostsFactory(posts__size=1)

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class SearchViewTest(TestCase):
    def setUp(self):
        self.feed = FeedWithPostsFactory(posts__size=5)

    def test_invalid_search(self):
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 302)

    def test_post_search(self):
        response = self.client.get("/search/?search=go&q=post&w=posts")
        self.assertEqual(response.status_code, 200)

    def test_author_search(self):
        response = self.client.get("/search/?search=go&q=author&w=authors")
        self.assertEqual(response.status_code, 200)

    def test_feed_search(self):
        response = self.client.get("/search/?search=go&q=feed&w=feeds")
        self.assertEqual(response.status_code, 200)

    def test_navbar_form_preserves_query_and_selection_after_search(self):
        response = self.client.get("/search/?q=Adam&w=authors")
        self.assertContains(response, 'value="Adam"')
        self.assertContains(response, '<option value="authors" selected>')

    def test_navbar_form_is_empty_on_non_search_page(self):
        response = self.client.get("/posts/")
        self.assertContains(response, 'name="q" value=""')
        self.assertNotContains(response, "selected>")
