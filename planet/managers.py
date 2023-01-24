# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from planet.utils import md5_hash, normalize_language, to_datetime


class FeedQuerySet(models.QuerySet):

    def search(self, query):
        return self.filter(title__icontains=query)

    def for_author(self, author):
        return self.filter(post__authors=author).distinct()


class FeedManager(models.Manager):
    def get_queryset(self):
        return FeedQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)

    def for_author(self, author):
        return self.get_queryset().for_author(author)

    def get_by_url(self, url):
        # Feed urls may be too long to index for some SQL databases. That's why we use a hash.
        guid = md5_hash(url)
        return self.model.objects.get(guid=guid)

    def create_from(self, feed_data, blog):
        feed = self.model()
        feed.url = feed_data.href
        feed.title = feed_data.feed.get("title", "--")
        feed.subtitle = feed_data.feed.get("subtitle")
        feed.rights = feed_data.feed.get("rights") or feed_data.feed.get("license")
        feed.guid = md5_hash(feed_data.feed.get("id") or feed.url)
        feed.language = normalize_language(feed_data.feed.get("language"))
        feed.etag = feed_data.get("etag") or None
        feed.last_modified = to_datetime(feed_data.get("updated_parsed"))
        feed.last_checked = timezone.now()
        feed.blog = blog
        feed.save()

        return feed


class BlogQuerySet(models.QuerySet):

    def for_author(self, author):
        return self.filter(feed__post__authors=author).distinct()

    def search(self, query):
        return self.filter(title__icontains=query)


BlogManager = BlogQuerySet.as_manager


class AuthorQuerySet(models.QuerySet):

    def for_blog(self, blog):
        return self.filter(post__feed__blog=blog).distinct()

    def search(self, query):
        return self.filter(name__icontains=query)


AuthorManager = AuthorQuerySet.as_manager


class PostQuerySet(models.QuerySet):

    def for_blog(self, blog):
        return self.filter(feed__blog=blog)

    def for_feed(self, feed):
        return self.filter(feed=feed)

    def for_author(self, author):
        return self.filter(authors=author)

    def search(self, query):
        return self.filter(title__icontains=query)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def for_blog(self, blog):
        return self.get_queryset().for_blog(blog)

    def for_feed(self, feed):
        return self.get_queryset().for_feed(feed)

    def for_author(self, author):
        return self.get_queryset().for_author(author)

    def search(self, query):
        return self.get_queryset().search(query)

    def get_by_url(self, url):
        guid = md5_hash(url)
        return self.model.objects.get(guid=guid)

    def create_from(self, entry_data, feed):
        post = self.model()
        post.title = entry_data.title
        post.url = entry_data.link
        post.guid = md5_hash(post.url)

        try:
            post.content = entry_data.summary
        except AttributeError:
            pass

        try:
            language = entry_data.summary_detail.language
        except AttributeError:
            language = feed.language

        post.language = normalize_language(language)

        try:
            post.date_published = to_datetime(entry_data.published_parsed)
        except AttributeError:
            post.date_published = timezone.now()

        post.feed = feed
        post.save()

        return post
