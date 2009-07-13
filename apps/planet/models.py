# -*- coding: utf-8 -*-

"""
    django-planet models

    Heavily based on Feedjack's [1] models by Gustavo Picón. Changes and addings
    inspired by Mark Pilgrim's Feedparser [2].

    [1] http://www.feedjack.org/
    [2] http://www.feedparser.org/
 
    Summary of changes:
    * Link model was dropped.
    * Site models replaced by django.contrib.sites.Site model :)
    * Tag model replaced by tagging.Tag model.
    * Added Blog model (a Blog may have several Feed objects related).
    * Subscriber model renamed to Author, and was modifyed since a Blog may
      have several authors. Authors may be of two types: author or contributor.
    * Feed model was changed. New attributes added to store info provided by
      Feedparser.
    * Added FeedLink, PostLink, Enclosure and Generator models to store info
      provided by Feedparser.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.sites.models import Site

import tagging

from planet.managers import (FeedManager, AuthorManager, BlogManager,
    PostManager, GeneratorManager, PostLinkManager, FeedLinkManager,
    EnclosureManager)


class Blog(models.Model):
    """
    A model to store primary info about a blog or website that which feed or
    feeds are aggregated to our planet
    """
    title = models.CharField(_("title"), max_length=255, blank=True)
    url = models.URLField(_("Url"), unique=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    site_objects = BlogManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ('title', 'url',)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.url)

class Generator(models.Model):
    """
    The software or website that has built a feed
    """
    name = models.CharField(_("Name"), max_length=100)
    link = models.URLField(_("Url"), blank=True, null=True) 
    version = models.CharField(_("Version"), max_length=5, blank=True, null=True)

    site_objects = GeneratorManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Generator")
        verbose_name_plural = _("Generators")
        ordering = ('name', 'version',)
        unique_together = (("name", "link", "version"), )

    def __unicode__(self):
        return u'%s %s (%s)' % (self.name, self.version or "", self.link or "--")


class Feed(models.Model):
    """
    A model to store detailed info about a parsed Atom or RSS feed
    """
    # a feed belongs to a blog
    blog = models.ForeignKey("planet.Blog", null=False, blank=False)
    # a site where this feed is published
    site = models.ForeignKey(Site)
    # url to retrieve this feed
    url = models.URLField(_("Url"), unique=True)
    # title attribute from Feedparser's Feed object
    title = models.CharField(_("Title"), max_length=255)
    # subtitle attribute from Feedparser's Feed object. aka tagline
    subtitle = models.TextField(_("Subtitle"), blank=True, null=True)
    # rights or license attribute from Feedparser's Feed object
    rights = models.CharField(_("Rights"), max_length=255, blank=True, null=True)
    # generator_detail attribute from Feedparser's Feed object
    generator = models.ForeignKey("planet.Generator", blank=True, null=True)
    # info attribute from Feedparser's Feed object
    info = models.CharField(_(""), max_length=255, blank=True, null=True)
    # language name or code. language attribute from Feedparser's Feed object
    language = models.CharField(_("Language"), max_length=50, blank=True, null=True)
    # global unique identifier for the feed
    guid = models.CharField(_("Global Unique Identifier"), max_length=255, blank=True, null=True)
    # icon attribute from Feedparser's Feed object
    icon_url = models.URLField(_("Icon URL"), blank=True, null=True)
    # image attribute from Feedparser's Feed object
    image_url = models.URLField(_("Image URL"), blank=True, null=True)

    # etag attribute from Feedparser's Feed object
    etag = models.CharField(_("Etag"), max_length=50, blank=True, null=True)
    # modified attribute from Feedparser's Feed object
    last_modified = models.DateTimeField(_("Last modified"), null=True, blank=True)
    # datetime when the feed was checked by last time
    last_checked = models.DateTimeField(_("Last checked"), null=True, blank=True)
    # in order to retrieve it or not
    is_active = models.BooleanField(_("Is active"), default=True,
        help_text=_("If disabled, this feed will not be further updated.") )

    site_objects = FeedManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ('title', 'url',)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.url)


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

    def __unicode__(self):
        author_type = self.is_contributor and "Contributor" or "Author"
        return u'%s (%s - %s)' % (
            self.author.name, author_type, self.post.title)
    

class Post(models.Model):
    """
    A feed contains a collection of posts. This model stores them.
    """
    feed = models.ForeignKey("planet.Feed", null=False, blank=False)
    title = models.CharField(_("Title"), max_length=255)
    authors = models.ManyToManyField("planet.Author", through=PostAuthorData)
    url = models.URLField(_("Url"))
    guid = models.CharField(_("Guid"), max_length=200, db_index=True)
    content = models.TextField(_("Content"))
    comments_url = models.URLField(_("Comments URL"), blank=True, null=True)
    
    date_modified = models.DateTimeField(_("Date modified"), null=True, blank=True)
    date_created = models.DateField(_("Date created"), auto_now_add=True)

    site_objects = PostManager()
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ('-date_modified',)
        unique_together = (('feed', 'guid'),)

    def __unicode__(self):
        return u"%s [%s]" % (self.title, self.feed.title)

# each Post object now will have got a .tags attribute!
tagging.register(Post)


class Author(models.Model):
    """
    An author is everyone who wrote or has contributed to write a post.
    """
    name = models.CharField(_("Name"), max_length=255, null=True, blank=True)
    email = models.EmailField(_("Author email"), blank=True)
    
    site_objects = AuthorManager()
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ('name', 'email')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.email,)


class FeedLink(models.Model):
    """
    Stores data contained in feedparser's feed.links for a given feed
    """
    feed = models.ForeignKey("planet.Feed")
    rel = models.CharField(_("Relation"), max_length=20)
    mime_type = models.CharField(_("MIME type"), max_length=50)
    link = models.URLField(_("Url")) 

    site_objects = FeedLinkManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Feed Link")
        verbose_name_plural = _("Feed Links")
        ordering = ("feed", "rel", "mime_type")
        unique_together = (("feed", "rel", "mime_type"), )

    def __unicode__(self):
        return u"%s %s (%s)" % (self.feed.title, self.rel, self.mime_type)


class PostLink(models.Model):
    """
    Stores data contained in feedparser's feed.entries[i].links for a given feed
    """
    post = models.ForeignKey("planet.Post")
    rel = models.CharField(_("Relation"), max_length=20)
    mime_type = models.CharField(_("MIME type"), max_length=50)
    link = models.URLField(_("Url")) 
    title = models.CharField(_("Title"), max_length=255) 

    site_objects = PostLinkManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Post Link")
        verbose_name_plural = _("Post Links")
        ordering = ("post", "title", "rel")
        unique_together = (("post", "rel", "mime_type"), )

    def __unicode__(self):
        return u"%s %s (%s)" % (self.title, self.rel, self.post)


class Enclosure(models.Model):
    """
    Stores data contained in feedparser's feed.entries[i].enclosures for a given feed
    """
    post = models.ForeignKey("planet.Post")
    length = models.CharField(_("Length"), max_length=20)
    mime_type = models.CharField(_("MIME type"), max_length=50)
    link = models.URLField(_("Url")) 

    site_objects = EnclosureManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Post Enclosure")
        verbose_name_plural = _("Post Enclosures")
        ordering = ("post", "mime_type", "link")
        unique_together = (("post", "link"), )

    def __unicode__(self):
        return u"%s [%s] (%s)" % (self.link, self.mime_type, self.post)

