# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from planet.models import Post, Blog, Feed, Author

from tagging.models import Tag


class BlogSitemap(Sitemap):

    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return Blog.objects.values_list("id", "title", "date_created")

    def lastmod(self, obj):
        return obj[2]

    def location(self, obj):
        slug = slugify(obj[1]) or "no-title"
        return reverse("planet.views.blog_detail",
            kwargs=dict(blog_id=obj[0], slug=slug))


class PostSitemap(Sitemap):

    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Post.objects.values_list("id", "title", "date_created")

    def lastmod(self, obj):
        return obj[2]

    def location(self, obj):
        slug = slugify(obj[1]) or "no-title"
        return reverse("planet.views.post_detail",
            kwargs=dict(post_id=obj[0], slug=slug))


class AuthorSitemap(Sitemap):

    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Author.objects.values_list("id", "name")

    def location(self, obj):
        slug = slugify(obj[1]) or "no-title"
        return reverse("planet.views.author_detail",
            kwargs=dict(author_id=obj[0], slug=slug))


class FeedSitemap(Sitemap):

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Feed.objects.values_list("id", "title", "last_modified")

    def lastmod(self, obj):
        return obj[2]

    def location(self, obj):
        slug = slugify(obj[1]) or "no-title"
        return reverse("planet.views.feed_detail",
            kwargs=dict(feed_id=obj[0], slug=slug))


class TagSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Tag.objects.values_list("name", flat=True)

    def lastmod(self, obj):
        return datetime.now()

    def location(self, obj):
        return reverse("planet.views.tag_detail",
            kwargs=dict(tag=obj))


planet_sitemaps_dict = {
    "blogs": BlogSitemap(),
    "posts": PostSitemap(),
    "authors": AuthorSitemap(),
    "feeds": FeedSitemap(),
    "tags": TagSitemap()
}
