# -*- coding: utf-8 -*-
import django

from django.db import models
from django.conf import settings


class FeedManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(FeedManager, self).get_queryset()
        return qs.filter(site=settings.SITE_ID, is_active=True)

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class FeedLinkManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(FeedLinkManager, self).get_queryset()
        return qs.filter(feed__site=settings.SITE_ID)

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class BlogManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(BlogManager, self).get_queryset()
        return qs.filter(feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class GeneratorManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(GeneratorManager, self).get_queryset()
        return qs.filter(feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class AuthorManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(AuthorManager, self).get_queryset()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class PostManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(PostManager, self).get_queryset()
        return qs.filter(feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class PostLinkManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(PostLinkManager, self).get_queryset()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset


class EnclosureManager(models.Manager):
    """
    """
    def get_queryset(self):
        qs = super(EnclosureManager, self).get_queryset()
        return qs.filter(post__feed__site=settings.SITE_ID).distinct()

    if django.VERSION < (1, 6):
        get_query_set = get_queryset
