from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from planet.models import Blog, Feed
from tests.factories import FeedFactory, PostAuthorDataFactory, PostFactory, AuthorFactory


class FeedAdminAddViewTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        self.client.force_login(self.superuser)
        self.add_url = reverse("admin:planet_feed_add")

    def test_add_page_shows_only_url_field(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
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
        change_url = reverse("admin:planet_feed_change", args=[feed.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="title"', response.content)
        self.assertIn(b'name="url"', response.content)


class FeedAdminAuthorsListTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        self.client.force_login(self.superuser)

    def test_authors_list_shows_author_links(self):
        author = AuthorFactory(name="Ada Lovelace")
        post = PostFactory(authors=[author])
        change_url = reverse("admin:planet_feed_change", args=[post.feed.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ada Lovelace", response.content)

    def test_authors_list_shows_no_authors_message(self):
        feed = FeedFactory()
        change_url = reverse("admin:planet_feed_change", args=[feed.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No authors", response.content)


class AuthorAdminFeedsListTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        self.client.force_login(self.superuser)

    def test_feeds_list_shows_feed_links(self):
        author = AuthorFactory()
        post = PostFactory(authors=[author])
        change_url = reverse("admin:planet_author_change", args=[author.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(post.feed.title.encode(), response.content)

    def test_feeds_list_shows_no_feeds_message(self):
        author = AuthorFactory()
        change_url = reverse("admin:planet_author_change", args=[author.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No feeds", response.content)


class PostAuthorDataAdminTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        self.client.force_login(self.superuser)

    def test_list_displays_author_name(self):
        author = AuthorFactory(name="Grace Hopper")
        PostAuthorDataFactory(author=author)
        list_url = reverse("admin:planet_postauthordata_changelist")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Grace Hopper", response.content)
