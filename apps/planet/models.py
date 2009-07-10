# -*- coding: utf-8 -*-

"""
django-planet models

heavily based on Feedjack's models by Gustavo Picón http://www.feedjack.org/

* Link model was dropped
* Site models replaced by django.contrib.sites.Site model :)
* Tag model replaced by tagging.Tag model
* Subscriber model renamed to Author, and was modifyed since a Blog may have
    several authors.
* Added Blog model (a Blog may have several Feed objects related)
* Feed models was changed and simplifyed
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _ 

from planet.managers import FeedManager, AuthorManager, BlogManager, PostManager


class Blog(models.Model):
    title = models.CharField(_("title"), max_length=255, blank=True)
    url = models.URLField(_("Url"), unique=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    site_objects = BlogManager()

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ('title', 'url',)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.url)


class Feed(models.Model):
    blog = models.ForeignKey(Blog, null=False, blank=False)
    site = models.ForeignKey(Site)
    
    url = models.URLField(_("Url"), unique=True)
    title = models.CharField(_("Title"), max_length=255, blank=True)
    tagline = models.TextField(_("Tagline"), blank=True)

    # http://feedparser.org/docs/http-etag.html
    etag = models.CharField(_("Etag"), max_length=50, blank=True)
    last_modified = models.DateTimeField(_("Last modified"), null=True, blank=True)
    last_checked = models.DateTimeField(_("Last checked"), null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True,
        help_text=_("If disabled, this feed will not be further updated.") )

    site_objects = FeedManager()

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ('name', 'url',)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.url)


class Post(models.Model):
    feed = models.ForeignKey(Feed, null=False, blank=False)
    title = models.CharField(_("Title"), max_length=255)
    content = models.TextField(_("Content"), blank=True)
    guid = models.CharField(_("Guid"), max_length=200, db_index=True)
    
    url = models.URLField(_("Url"), )
    comments_url = models.URLField(_("Comments URL"), blank=True)
    
    date_modified = models.DateTimeField(_("Date modified"), null=True, blank=True)
    date_created = models.DateField(_("Date created"), auto_now_add=True)

    site_objects = PostManager()
    
    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ('-date_modified',)
        unique_together = (('feed', 'guid'),)

    def __unicode__(self):
        return self.title


class Author(models.Model):
    blog = models.ForeignKey(Blog)

    name = models.CharField(_("Name"), max_length=255, null=True, blank=True,
        help_text=_("Keep blank to use the Blog\'s original name.") )
    is_active = models.BooleanField(_("Is active"), default=True,
        help_text=_("If disabled, this subscriber will not appear in the site or '
        'in the site\'s feed.") )
    email = models.EmailField(_("Author email"), blank=True)

    site_objects = AuthorManager()
    
    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ('name', 'blog')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.blog,)
