import logging

from django.apps import apps
from django.db import models
from django.utils import timezone

from planet.utils import md5_hash, normalize_language, to_datetime

logger = logging.getLogger(__name__)


class FeedQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def search(self, query):
        return self.filter(title__icontains=query)

    def for_author(self, author):
        return self.filter(post__authors=author).distinct()


class FeedManager(models.Manager):
    def get_queryset(self):
        return FeedQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

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


class BlogManager(models.Manager):
    def get_queryset(self):
        return BlogQuerySet(self.model, using=self._db)

    def for_author(self, author):
        return self.get_queryset().for_author(author)

    def search(self, query):
        return self.get_queryset().search(query)

    def get_or_create_from_feed(self, feed_data):
        return self.get_or_create(
            url=feed_data.feed.link,
            defaults={"title": feed_data.feed.title},
        )


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

    def with_relations(self):
        return self.select_related("feed", "feed__blog").prefetch_related("authors")


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

    def with_relations(self):
        return self.get_queryset().with_relations()

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

    def create_authors_for_post(self, post, authors_data):
        Author = apps.get_model("planet", "Author")
        PostAuthorData = apps.get_model("planet", "PostAuthorData")

        for author_dict in authors_data:
            try:
                name = author_dict["name"].strip()
            except KeyError:
                logger.debug("Author entry missing 'name' key, skipping: %s", author_dict)
                continue

            if name:
                author, _ = Author.objects.get_or_create(name=name)
                PostAuthorData.objects.create(post=post, author=author)

    def create_with_authors(self, entry_data, feed):
        post = self.create_from(entry_data, feed)
        self.create_authors_for_post(post, entry_data.get("authors", []))
        return post
