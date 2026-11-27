from django.template import Context, Template
from django.test import TestCase

from .factories import AuthorFactory, FeedFactory, PostFactory


class AuthorsForFeedTagTest(TestCase):
    """{% authors_for_feed %} broke with AttributeError when manager methods moved to QuerySets."""

    def test_renders_links_to_authors_of_the_feed(self):
        author = AuthorFactory(name="Ada Lovelace")
        feed = FeedFactory()
        PostFactory(feed=feed, authors=[author])

        out = Template("{% load planet_tags %}{% authors_for_feed feed %}").render(Context({"feed": feed}))

        self.assertIn("Authors for this feed", out)
        self.assertIn(author.name, out)
        self.assertIn(author.get_absolute_url(), out)

    def test_excludes_authors_from_other_feeds(self):
        other_author = AuthorFactory(name="Grace Hopper")
        PostFactory(authors=[other_author])  # post in a different feed

        out = Template("{% load planet_tags %}{% authors_for_feed feed %}").render(Context({"feed": FeedFactory()}))

        self.assertNotIn(other_author.name, out)
