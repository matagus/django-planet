# -*- coding: utf-8 -*-

"""
    django-planet models

    Heavily based on Feedjack's [1] models by Gustavo Picón. Changes and addings
    inspired by Mark Pilgrim's Feedparser [2].

    [1] http://www.feedjack.org/
    [2] http://www.feedparser.org/
"""

# python 3.x compatibility helpers
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

import feedparser
from datetime import datetime
from time import mktime, struct_time

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings
from django.db.models.signals import pre_delete
from django.template.defaultfilters import slugify

# Patch for handle new and old version of django-tagging
try:
    from tagging import register
except ImportError:
    from tagging.registry import register

from tagging.models import Tag

from planet.managers import (FeedManager, AuthorManager, BlogManager,
    PostManager, GeneratorManager, PostLinkManager, FeedLinkManager,
    EnclosureManager)


def _get_user_model():
    try:
        # New sinc Dajngo 1.5
        return settings.AUTH_USER_MODEL
    except AttributeError:
        # Django < 1.5
        return "auth.User"


@python_2_unicode_compatible
class Blog(models.Model):
    """
    A model to store primary info about a blog or website that which feed or
    feeds are aggregated to our planet
    """

    title = models.CharField(_("title"), max_length=255, blank=True, db_index=True)
    url = models.URLField(_("Url"), unique=True, db_index=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    owner = models.ForeignKey(_get_user_model(), null=True, blank=True)

    site_objects = BlogManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ('title', 'url',)

    def __str__(self):
        return '{} ({})'.format(self.title, self.url)

    @models.permalink
    def get_absolute_url(self):
        return ('planet.views.blog_detail', [str(self.id), self.get_slug()])

    def get_slug(self):
        return slugify(self.title) or "no-title"


@python_2_unicode_compatible
class Generator(models.Model):
    """
    The software or website that has built a feed
    """
    name = models.CharField(_("Name"), max_length=100)
    link = models.URLField(_("Url"), blank=True, null=True)
    version = models.CharField(_("Version"), max_length=200, blank=True, null=True)

    site_objects = GeneratorManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Generator")
        verbose_name_plural = _("Generators")
        ordering = ('name', 'version',)
        unique_together = (("name", "link", "version"), )

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.version or "", self.link or "--")


@python_2_unicode_compatible
class Category(models.Model):
    """
    Define Categories for Feeds. In this way a site can manage many
    aggregator/planet
    """
    title = models.CharField(_("Category Title"), max_length=100, unique=True)
    date_created = models.DateField(_("Date created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Feed Category")
        verbose_name_plural = _("Feed Categories")
        ordering = ('title', 'date_created')

    def __str__(self):
        return "{}".format(self.title)


@python_2_unicode_compatible
class Feed(models.Model):
    """
    A model to store detailed info about a parsed Atom or RSS feed
    """
    # a feed belongs to a blog
    blog = models.ForeignKey("planet.Blog", null=True, blank=True)
    # a site where this feed is published
    site = models.ForeignKey(Site, null=True, blank=True, db_index=True)
    # url to retrieve this feed
    url = models.URLField(_("Url"), unique=True, db_index=True)
    # title attribute from Feedparser's Feed object
    title = models.CharField(_("Title"), max_length=255, db_index=True,
        blank=True, null=True)
    # subtitle attribute from Feedparser's Feed object. aka tagline
    subtitle = models.TextField(_("Subtitle"), blank=True, null=True)
    # rights or license attribute from Feedparser's Feed object
    rights = models.CharField(_("Rights"), max_length=255, blank=True,
                              null=True)
    # generator_detail attribute from Feedparser's Feed object
    generator = models.ForeignKey("planet.Generator", blank=True, null=True)
    # info attribute from Feedparser's Feed object
    info = models.CharField(_("Infos"), max_length=255, blank=True, null=True)
    # language name or code. language attribute from Feedparser's Feed object
    language = models.CharField(_("Language"), max_length=50, blank=True,
                                null=True)
    # global unique identifier for the feed
    guid = models.CharField(_("Global Unique Identifier"), max_length=32,
        blank=True, null=True, db_index=True)
    # icon attribute from Feedparser's Feed object
    icon_url = models.URLField(_("Icon URL"), blank=True, null=True)
    # image attribute from Feedparser's Feed object
    image_url = models.URLField(_("Image URL"), blank=True, null=True)

    # etag attribute from Feedparser's Feed object
    etag = models.CharField(_("Etag"), max_length=50, blank=True,
        null=True, db_index=True)
    # modified attribute from Feedparser's Feed object
    last_modified = models.DateTimeField(_("Last modified"), null=True,
        blank=True, db_index=True)
    # datetime when the feed was checked by last time
    last_checked = models.DateTimeField(_("Last checked"), null=True,
                                        blank=True)
    # in order to retrieve it or not
    is_active = models.BooleanField(_("Is active"), default=True,
                                    db_index=True,
        help_text=_("If disabled, this feed will not be further updated."))

    category = models.ForeignKey(Category, blank=True, null=True,
                                 db_index=True)

    site_objects = FeedManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ('title', )

    def save(self, *args, **kwargs):
        if not self.blog:
            self.modified = self.etag = None

            try:
                USER_AGENT = settings.PLANET["USER_AGENT"]
            except (KeyError, AttributeError):
                print("""Please set the PLANET = {"USER_AGENT": <string>} in your settings.py""")
                exit(0)

            document = feedparser.parse(self.url, agent=USER_AGENT,
                                        modified=self.modified, etag=self.etag)

            self.site = Site.objects.get(pk=settings.SITE_ID)

            self.title = document.feed.get("title", "--")
            self.subtitle = document.feed.get("subtitle")
            blog_url = document.feed.get("link")
            self.rights = document.feed.get("rights") or document.feed.get("license")
            self.info = document.feed.get("info")
            self.guid = document.feed.get("id")
            self.image_url = document.feed.get("image", {}).get("href")
            self.icon_url = document.feed.get("icon")
            self.language = document.feed.get("language")
            self.etag = document.get("etag", '')

            self.last_modified = document.get("updated_parsed", datetime.now())
            if isinstance(self.last_modified, struct_time):
                self.last_modified = datetime.fromtimestamp(mktime(self.last_modified))

            self.blog, created = Blog.objects.get_or_create(
                url=blog_url, defaults={"title": self.title})

            generator_dict = document.feed.get("generator_detail", {})

            if generator_dict:
                self.generator, created = Generator.objects.get_or_create(
                    name=generator_dict.get("name", "--"),
                    link=generator_dict.get("link"),
                    version=generator_dict.get("version"))
            else:
                self.generator = None

        super(Feed, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.title, self.url)

    @models.permalink
    def get_absolute_url(self):
        return ('planet.views.feed_detail', [str(self.id), self.get_slug()])

    def get_slug(self):
        return slugify(self.title) or "no-title"


@python_2_unicode_compatible
class PostAuthorData(models.Model):
    """
    This is the intermediate model that holds the information of the post authors
    """
    post = models.ForeignKey("planet.Post")
    author = models.ForeignKey("planet.Author")
    # True if this author is a contributor. False to tell he is the original
    # author of ths post
    is_contributor = models.BooleanField(_("Is Contributor?"), default=False)
    date_created = models.DateField(_("Date created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Post Author Data")
        verbose_name_plural = _("Post Author Data")
        ordering = ("author", "post", "is_contributor")

    def __str__(self):
        author_type = self.is_contributor and "Contributor" or "Author"
        return '{} ({} - {})'.format(
            self.author.name, author_type, self.post.title)


@python_2_unicode_compatible
class Post(models.Model):
    """
    A feed contains a collection of posts. This model stores them.
    """
    feed = models.ForeignKey("planet.Feed", null=False, blank=False)
    title = models.CharField(_("Title"), max_length=255, db_index=True)
    authors = models.ManyToManyField("planet.Author", through=PostAuthorData)
    url = models.URLField(_("Url"), max_length=1000, db_index=True)
    guid = models.CharField(_("Guid"), max_length=32, db_index=True)
    content = models.TextField(_("Content"))
    comments_url = models.URLField(_("Comments URL"), blank=True, null=True)

    date_modified = models.DateTimeField(_("Date modified"), null=True,
        blank=True, db_index=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    site_objects = PostManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ('-date_created', '-date_modified')
        unique_together = (('feed', 'guid'),)

    def __str__(self):
        return "{} [{}]".format(self.title, self.feed.title)

    @models.permalink
    def get_absolute_url(self):
        return ('planet.views.post_detail', [str(self.id), self.get_slug()])

    def get_slug(self):
        return slugify(self.title) or "no-title"

# each Post object now will have got a .tags attribute!
register(Post)

# Deleting all asociated tags.
def delete_asociated_tags(sender, **kwargs):
    Tag.objects.update_tags(kwargs['instance'], None)
pre_delete.connect(delete_asociated_tags, sender=Post)


@python_2_unicode_compatible
class Author(models.Model):
    """
    An author is everyone who wrote or has contributed to write a post.
    """
    name = models.CharField(_("Name"), max_length=255, null=True,
        blank=True, db_index=True)
    email = models.EmailField(_("Author email"), blank=True, db_index=True)
    profile_url = models.URLField(_("Profile URL"), blank=True, null=True)

    site_objects = AuthorManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ('name', 'email')

    def __str__(self):
        return "{} ({})".format(self.name, self.email)

    @models.permalink
    def get_absolute_url(self):
        return ('planet.views.author_detail', [str(self.id), self.get_slug()])

    def get_slug(self):
        return slugify(self.name) or "no-title"


@python_2_unicode_compatible
class FeedLink(models.Model):
    """
    Stores data contained in feedparser's feed.links for a given feed
    """
    feed = models.ForeignKey("planet.Feed")
    rel = models.CharField(_("Relation"), max_length=50, db_index=True)
    mime_type = models.CharField(_("MIME type"), max_length=50, db_index=True)
    link = models.URLField(_("Url"), max_length=500, db_index=True)

    site_objects = FeedLinkManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Feed Link")
        verbose_name_plural = _("Feed Links")
        ordering = ("feed", "rel", "mime_type")
        #unique_together = (("feed", "rel", "mime_type", "link"), )

    def __str__(self):
        return "{} {} ({})".format(self.feed.title, self.rel, self.mime_type)


class PostLink(models.Model):
    """
    Stores data contained in feedparser's feed.entries[i].links for a given feed
    """
    post = models.ForeignKey("planet.Post")
    rel = models.CharField(_("Relation"), max_length=50, db_index=True)
    mime_type = models.CharField(_("MIME type"), max_length=50, db_index=True)
    link = models.URLField(_("Url"), max_length=500, db_index=True)
    title = models.CharField(_("Title"), max_length=255, db_index=True)

    site_objects = PostLinkManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Post Link")
        verbose_name_plural = _("Post Links")
        ordering = ("post", "title", "rel")
        #unique_together = (("post", "rel", "mime_type", "title"), )

    def __str__(self):
        return "{} {} ({})".format(self.title, self.rel, self.post)


@python_2_unicode_compatible
class Enclosure(models.Model):
    """
    Stores data contained in feedparser's feed.entries[i].enclosures for a given feed
    """
    post = models.ForeignKey("planet.Post")
    length = models.CharField(_("Length"), max_length=20)
    mime_type = models.CharField(_("MIME type"), max_length=50, db_index=True)
    link = models.URLField(_("Url"), max_length=500, db_index=True)

    site_objects = EnclosureManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Post Enclosure")
        verbose_name_plural = _("Post Enclosures")
        ordering = ("post", "mime_type", "link")
        #unique_together = (("post", "link", "mime_type"), )

    def __str__(self):
        return "{} [{}] ({})".format(self.link, self.mime_type, self.post)

