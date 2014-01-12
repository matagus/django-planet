from django.test import TestCase
from django.contrib.sites.models import Site

from planet.tests.factories import PostFactory, SiteFactory, FeedFactory
from planet.models import Post


class PostManagerTestCase(TestCase):

    def setUp(self):
        self.other_site = SiteFactory.create()
        self.other_feed = FeedFactory.create(site=self.other_site)
        self.other_posts = PostFactory.create_batch(size=4, feed=self.other_feed)

        self.my_site = Site.objects.get(pk=1)
        self.my_feed = FeedFactory.create(site=self.my_site)
        self.site_posts = PostFactory.create_batch(size=5, feed=self.my_feed)

    def test_post_count(self):
        self.assertEquals(Post.objects.count(), 9)
        self.assertEquals(Post.site_objects.count(), 5)
