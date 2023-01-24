# -*- coding: utf-8 -*-
"""
    django-planet models

    Heavily based on Feedjack's [1] models by Gustavo Picón. Changes and
    addings inspired by Mark Pilgrim's Feedparser [2].

    [1] http://www.feedjack.org/
    [2] http://www.feedparser.org/
"""

import feedparser

from datetime import datetime
from time import mktime, struct_time

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from planet.managers import AuthorManager, BlogManager, FeedManager, PostManager
from planet.settings import PLANET_CONFIG


class Blog(models.Model):
    """
    A model to store primary info about a blog or website that which feed or
    feeds are aggregated to our planet
    """

    title = models.CharField(_("title"), max_length=255)
    url = models.URLField(_("Url"), unique=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    objects = BlogManager()

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ('title', 'url', )
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['url']),
            models.Index(fields=['-date_created']),
            models.Index(fields=['title', 'url']),
        ]

    def __str__(self):
        return f"{self.title} ({self.url})"

    def get_absolute_url(self):
        kwargs = dict(blog_id=self.id, slug=self.get_slug())
        return reverse('planet:blog-detail', kwargs=kwargs)

    def get_slug(self):
        return slugify(self.title) or "no-title"


class Feed(models.Model):
    """
    A model to store detailed info about a parsed Atom or RSS feed
    """
    # a feed belongs to a blog
    blog = models.ForeignKey("planet.Blog", on_delete=models.CASCADE)
    # url to retrieve this feed
    url = models.URLField(_("Url"), unique=True)
    # title attribute from Feedparser's Feed object
    title = models.CharField(_("Title"), max_length=255)
    # subtitle attribute from Feedparser's Feed object. aka tagline
    subtitle = models.TextField(_("Subtitle"), blank=True, null=True)
    # rights or license attribute from Feedparser's Feed object
    rights = models.CharField(
        _("Rights"), max_length=255, blank=True, null=True
    )
    # language name or code. language attribute from Feedparser's Feed object
    language = models.CharField(
        _("Language"), max_length=50, blank=True, null=True
    )
    # global unique identifier for the feed
    guid = models.CharField(_("Global Unique Identifier"), max_length=32, unique=True)

    # etag attribute from Feedparser's Feed object
    etag = models.CharField(
        _("Etag"), max_length=50, blank=True, null=True
    )
    # modified attribute from Feedparser's Feed object
    last_modified = models.DateTimeField(
        _("Last modified"), null=True, blank=True
    )
    # datetime when the feed was checked by last time
    last_checked = models.DateTimeField(
        _("Last checked"), null=True, blank=True
    )
    # in order to retrieve it or not
    is_active = models.BooleanField(
        _("Is active"), default=True,
        help_text=_("If disabled, this feed will not be further updated.")
    )

    objects = FeedManager()

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ('title', )
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['guid']),
            models.Index(fields=['etag']),
            models.Index(fields=['-last_modified']),
            models.Index(fields=['-last_checked']),
            models.Index(fields=['is_active']),
        ]

    def should_update(self):
        # TO-DO: evaluate logic using etag, last_checked, last_modified and is_active!
        return True

    def retrieve_and_update(self):
        if not self.should_update():
            return None

        try:
            document = feedparser.parse(self.url, agent=PLANET_CONFIG['USER_AGENT'])
        except Exception:
            # TO-DO !!!!
            pass

        self.etag = document.get("etag")
        self.last_modified = document.get("updated_parsed", timezone.now())

        if isinstance(self.last_modified, struct_time):
            self.last_modified = datetime.fromtimestamp(mktime(self.last_modified))

        self.last_checked = timezone.now()
        self.save()

        # try to create new posts!!!
        pass

        return self

    def __str__(self):
        return f"{self.title} ({self.url})"

    def get_absolute_url(self):
        kwargs = dict(feed_id=self.id, slug=self.get_slug())
        return reverse('planet:feed-detail', kwargs=kwargs)

    def get_slug(self):
        return slugify(self.title) or "no-title"


class PostAuthorData(models.Model):
    """
    This is the intermediate model that holds post authors information
    """
    post = models.ForeignKey("planet.Post", on_delete=models.CASCADE)
    author = models.ForeignKey("planet.Author", on_delete=models.CASCADE)
    # True if this author is a contributor. False to tell he is the original
    # author of ths post
    is_contributor = models.BooleanField(_("Is Contributor?"), default=False)
    date_created = models.DateField(_("Date created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Post Author Data")
        verbose_name_plural = _("Post Author Data")
        ordering = ("author", "post", "is_contributor")
        indexes = [
            models.Index(fields=['author', 'post', 'is_contributor']),
        ]

    def __str__(self):
        author_type = self.is_contributor and "Contributor" or "Author"
        return f"{self.author.name} ({author_type} - {self.post.title})"


class Post(models.Model):
    """
    A feed contains a collection of posts. This model stores them.
    """
    feed = models.ForeignKey("planet.Feed", on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=255)
    authors = models.ManyToManyField("planet.Author", through=PostAuthorData)
    url = models.URLField(_("Url"), max_length=1000)
    guid = models.CharField(_("Guid"), max_length=32, unique=True)
    content = models.TextField(_("Content"))
    language = models.CharField(_("Language"), max_length=50, blank=True, null=True)
    comments_url = models.URLField(_("Comments URL"), blank=True, null=True)
    date_published = models.DateTimeField(_("Date Published"))
    date_modified = models.DateTimeField(_("Date Modified"), auto_now=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    objects = PostManager()

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['-date_published']
        unique_together = [['feed', 'guid']]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['guid']),
            models.Index(fields=['language']),
            models.Index(fields=['-date_modified']),
            models.Index(fields=['-date_created']),
            models.Index(fields=['-date_published']),
        ]

    def __str__(self):
        return "{} [{}]".format(self.title, self.feed.title)

    def get_absolute_url(self):
        kwargs = dict(post_id=self.id, slug=self.get_slug())
        return reverse('planet:post-detail', kwargs=kwargs)

    def get_slug(self):
        return slugify(self.title) or "no-title"


class Author(models.Model):
    """
    An author is everyone who wrote or has contributed to write a post.
    """
    name = models.CharField(_("Name"), max_length=255, null=True, blank=True)
    email = models.EmailField(_("Author email"), blank=True, db_index=True)
    profile_url = models.URLField(_("Profile URL"), blank=True, null=True)

    objects = AuthorManager()

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ('name', 'email')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['name', 'email']),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def get_absolute_url(self):
        kwargs = dict(author_id=self.id, slug=self.get_slug())
        return reverse('planet:author-detail', kwargs=kwargs)

    def get_slug(self):
        return slugify(self.name) or "no-title"
