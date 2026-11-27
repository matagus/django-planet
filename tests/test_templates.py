from django.template import RequestContext, Template
from django.test import RequestFactory, TestCase

from .factories import FeedFactory, FeedWithPostsFactory, PostFactory


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


class PaginationTemplateTest(TestCase):
    """planet ships a Bootstrap-styled override of pagination/pagination.html."""

    def test_post_list_renders_bootstrap_pagination(self):
        FeedWithPostsFactory(posts__size=12)

        response = self.client.get("/posts/")

        self.assertContains(response, '<ul class="pagination pagination-sm justify-content-center flex-wrap">')
        self.assertContains(response, '<li class="page-item active" aria-current="page">')
        self.assertContains(response, '<a class="page-link text-success" href="?page=2"')

    def test_current_page_is_active_and_previous_disabled_on_first_page(self):
        FeedWithPostsFactory(posts__size=12)

        response = self.client.get("/posts/?page=2")

        self.assertContains(response, '<span class="page-link bg-success border-success">2</span>')
        self.assertContains(response, 'href="?page=1"')

    def test_single_page_renders_no_pagination_nav(self):
        FeedWithPostsFactory(posts__size=2)

        response = self.client.get("/posts/")

        self.assertNotContains(response, '<ul class="pagination')


class BlogBreadcrumbPartialTest(TestCase):
    """planet/blocks/breadcrumb_blog.html is shared by the feed and post detail views."""

    def test_feed_detail_links_to_blogs_list_and_owning_blog(self):
        feed = FeedFactory()

        response = self.client.get(feed.get_absolute_url())

        self.assertContains(response, "/blogs/")
        self.assertContains(response, feed.blog.get_absolute_url())
        self.assertContains(response, feed.blog.title)

    def test_post_detail_links_to_blogs_list_and_owning_blog(self):
        post = PostFactory()

        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, "/blogs/")
        self.assertContains(response, post.feed.blog.get_absolute_url())
        self.assertContains(response, post.feed.blog.title)
