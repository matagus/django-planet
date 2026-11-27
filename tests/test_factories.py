from django.test import TestCase

from planet.models import Post

from .factories import DEFAULT_POSTS_PER_FEED, AuthorFactory, FeedWithPostsFactory


class FeedWithPostsFactoryTest(TestCase):
    def test_creates_default_number_of_posts_for_the_feed(self):
        feed = FeedWithPostsFactory()

        self.assertEqual(Post.objects.for_feed(feed).count(), DEFAULT_POSTS_PER_FEED)

    def test_posts_size_kwarg_controls_how_many_posts_are_created(self):
        feed = FeedWithPostsFactory(posts__size=5)

        self.assertEqual(Post.objects.for_feed(feed).count(), 5)

    def test_posts_kwargs_are_forwarded_to_post_factory(self):
        author = AuthorFactory()
        feed = FeedWithPostsFactory(posts__size=2, posts__authors=[author])

        self.assertEqual(Post.objects.for_feed(feed).for_author(author).count(), 2)
