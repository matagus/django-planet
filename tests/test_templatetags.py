from django.template import Context, Template
from django.test import TestCase
from django.utils import timezone

from .factories import AuthorFactory, FeedFactory, FeedWithPostsFactory, PostFactory


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


class SidebarNavTagsTest(TestCase):
    """The four sidebar inclusion tags share planet/blocks/nav_list.html."""

    def render_tag(self, source, **context):
        return Template("{% load planet_tags %}" + source).render(Context(context))

    def test_authors_for_feed_empty_list_renders_nothing(self):
        out = self.render_tag("{% authors_for_feed feed %}", feed=FeedFactory())

        self.assertNotIn("<nav", out)

    def test_feeds_for_author_lists_only_that_authors_feeds(self):
        author = AuthorFactory()
        feed = FeedWithPostsFactory(posts__size=1, posts__authors=[author])
        other_feed = FeedFactory()

        out = self.render_tag("{% feeds_for_author author %}", author=author)

        self.assertIn("Feeds", out)
        self.assertIn(feed.title, out)
        self.assertIn(feed.get_absolute_url(), out)
        self.assertNotIn(other_feed.title, out)

    def test_recent_posts_links_to_posts(self):
        post = PostFactory(title="A recent post")

        out = self.render_tag("{% recent_posts %}")

        self.assertIn("Recent Posts", out)
        self.assertIn(post.title, out)
        self.assertIn(post.get_absolute_url(), out)

    def test_recent_blogs_lists_published_blogs_only(self):
        published_feed = FeedWithPostsFactory(posts__size=1, last_checked=timezone.now())
        unpublished_feed = FeedFactory(last_checked=None)  # its blog is not published

        out = self.render_tag("{% recent_blogs %}")

        self.assertIn("Recently Added Blogs", out)
        self.assertIn(published_feed.blog.title, out)
        self.assertNotIn(unpublished_feed.blog.title, out)

    def test_labels_are_escaped(self):
        item = type("X", (), {"title": "<script>x</script>", "get_absolute_url": "/x/"})()
        source = '{% include "planet/blocks/nav_list.html" with items=items title="T" label_field="title" %}'

        out = Template(source).render(Context({"items": [item]}))

        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)


class AttrTagTest(TestCase):
    def test_resolves_attribute_by_name(self):
        obj = type("X", (), {"title": "T"})()

        out = Template('{% load planet_tags %}{% attr obj "title" %}').render(Context({"obj": obj}))

        self.assertEqual(out.strip(), "T")

    def test_resolves_methods_without_args(self):
        obj = type("X", (), {"get_absolute_url": lambda self: "/x/"})()

        out = Template('{% load planet_tags %}{% attr obj "get_absolute_url" %}').render(Context({"obj": obj}))

        self.assertEqual(out.strip(), "/x/")

    def test_missing_attribute_is_blank_not_error(self):
        out = Template('{% load planet_tags %}{% attr obj "nope" %}').render(Context({"obj": object()}))

        self.assertEqual(out.strip(), "")
