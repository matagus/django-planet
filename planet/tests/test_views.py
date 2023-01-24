# -*- coding: utf-8 -*-
from django.test import TestCase

from planet.tests.factories import (
    BlogFactory, FeedFactory, PostFactory, AuthorFactory
)


class BlogViewsTest(TestCase):

    def setUp(self):
        self.blog = BlogFactory.create(title="Blog-1")
        self.feed = FeedFactory.create(title="Feed-1", blog=self.blog)

    def test_list(self):
        response = self.client.get("/blogs/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get("/blogs/1/")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/blogs/1/blog-1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blogs/2/other-blog/")
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.blog.delete()
        self.feed.delete()


class FeedViewsTest(TestCase):

    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")

        self.post = PostFactory.create(feed=self.feed)
        self.post.tags = "tag1, tag2"

    def test_list(self):
        response = self.client.get("/feeds/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get("/feeds/1/")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/feeds/1/feed-1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/feeds/2/other-feed/")
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.feed.delete()
        self.post.delete()


class PostViewsTest(TestCase):

    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post = PostFactory.create(feed=self.feed)

    def test_list(self):
        response = self.client.get("/posts/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get("/posts/1/")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/posts/1/post-1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/posts/2/other-post/")
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.post.delete()
        self.feed.delete()


class AuthorViewsTest(TestCase):

    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.author = AuthorFactory.create(name="Author-1")
        self.post_list = PostFactory.create_batch(size=3, feed=self.feed, authors=[self.author])

        post = self.post_list[0]
        post.tags = "tag1, tag2"

    def test_list(self):
        response = self.client.get("/authors/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get("/authors/1/")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/authors/1/author-1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/authors/2/other-author/")
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.author.delete()
        self.feed.delete()


class IndexViewTest(TestCase):

    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post = PostFactory.create(feed=self.feed)

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.post.delete()
        self.feed.delete()


class SearchViewTest(TestCase):

    def setUp(self):
        self.feed = FeedFactory.create(title="Feed-1")
        self.post_list = PostFactory.create_batch(size=5, feed=self.feed)

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

    def tearDown(self):
        self.feed.delete()
