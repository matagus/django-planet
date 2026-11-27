from django.template import RequestContext, Template
from django.test import RequestFactory, TestCase

from .factories import FeedWithPostsFactory, PostFactory


class PostListPartialTest(TestCase):
    """planet/posts/blocks/post_list.html is shared by the blog/feed/author/post views."""

    def render_partial(self, source='{% include "planet/posts/blocks/post_list.html" %}', **context):
        # {% autopaginate %} reads the request, so render with a RequestContext.
        return Template(source).render(RequestContext(RequestFactory().get("/"), context))

    def test_renders_one_summary_per_post(self):
        feed = FeedWithPostsFactory(posts__size=2)
        posts = list(feed.post_set.all())

        out = self.render_partial(posts=posts)

        for post in posts:
            self.assertIn(post.get_absolute_url(), out)
        self.assertEqual(out.count("[Archived Version]"), 2)

    def test_default_wrapper_classes(self):
        out = self.render_partial(posts=[PostFactory()])

        self.assertIn('<div class="container px-0">', out)
        self.assertIn('<div class="post row">', out)

    def test_wrapper_classes_can_be_overridden_via_include_with(self):
        out = self.render_partial(
            '{% include "planet/posts/blocks/post_list.html" '
            'with container_class="content pd-0" post_wrapper_class="row post" %}',
            posts=[PostFactory()],
        )

        self.assertIn('<div class="content pd-0">', out)
        self.assertIn('<div class="row post">', out)

    def test_empty_posts_render_no_summaries(self):
        out = self.render_partial(posts=[])

        self.assertNotIn("[Archived Version]", out)

    def test_views_paginate_through_the_shared_partial(self):
        FeedWithPostsFactory(posts__size=12)

        response = self.client.get("/posts/")

        self.assertContains(response, "[Archived Version]", count=10)  # 10 per page
        self.assertContains(response, "?page=2")  # {% paginate %} links to the next page
