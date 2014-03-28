from django.contrib.sites.models import Site
from django.test import TestCase

from planet.tests.factories import AuthorFactory, FeedFactory, PostFactory, SiteFactory
from planet.models import Blog, Feed, Post, Author


class ManagersTestCase(TestCase):

    def setUp(self):
        self.author1 = AuthorFactory.create()
        self.author2 = AuthorFactory.create()

        self.other_site = SiteFactory.create()
        self.other_feed = FeedFactory.create(site=self.other_site)
        self.other_posts = PostFactory.create_batch(size=4, feed=self.other_feed, authors=[self.author1])

        self.my_site = Site.objects.get(pk=1)
        self.my_feed = FeedFactory.create(site=self.my_site)
        self.site_posts = PostFactory.create_batch(size=5, feed=self.my_feed, authors=[self.author2])

    def test_posts(self):
        self.assertEqual(Post.objects.count(), 9)
        self.assertEqual(Post.site_objects.count(), 5)

        site_posts_qs = Post.site_objects.all()
        for post in self.site_posts:
            self.assertTrue(post in site_posts_qs)

    def test_feeds(self):
        self.assertEqual(Feed.objects.count(), 2)
        self.assertEqual(Feed.site_objects.count(), 1)
        self.assertTrue(self.my_feed in Feed.site_objects.all())

    def test_blogs(self):
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(Blog.site_objects.count(), 1)
        self.assertTrue(self.my_feed.blog in Blog.site_objects.all())

    def test_author_count(self):
        self.assertEqual(Author.objects.count(), 2)

    def test_author_posts_counts(self):
        self.assertEqual(Post.objects.filter(authors=self.author1).count(), 4)
        self.assertEqual(Post.objects.filter(authors=self.author2).count(), 5)
