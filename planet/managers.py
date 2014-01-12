# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings


class FeedManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(FeedManager, self).get_query_set()
        return qs.filter(site=settings.SITE_ID, is_active=True)


class FeedLinkManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(FeedLinkManager, self).get_query_set()
        return qs.filter(feed__site=settings.SITE_ID)


class BlogManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(BlogManager, self).get_query_set()
        return qs.filter(feed__site=settings.SITE_ID).distinct()


class GeneratorManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(GeneratorManager, self).get_query_set()
        return qs.filter(feed__site=settings.SITE_ID).distinct()


class AuthorManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(AuthorManager, self).get_query_set()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()


class PostManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(PostManager, self).get_query_set()
        return qs.filter(feed__site=settings.SITE_ID).distinct()


class PostLinkManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(PostLinkManager, self).get_query_set()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()


class EnclosureManager(models.Manager):
    """
    """
    def get_query_set(self):
        qs = super(EnclosureManager, self).get_query_set()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()
