from django.test import TestCase

from .factories import AuthorFactory, FeedFactory, PostFactory
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
