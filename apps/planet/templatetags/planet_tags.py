#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from django import template
from django.db.models import Count, Max, F

from planet.models import Author, Feed, Blog

from tagging.models import Tag


register = template.Library()


@register.inclusion_tag('authors/blocks/list_for_tag.html')
def authors_about(tag):
    authors = Author.site_objects.filter(post=1).distinct()

    return {"authors": authors, "tag": tag}


@register.inclusion_tag('feeds/blocks/list_for_tag.html')
def feeds_about(tag):
    feeds_list = Feed.site_objects.filter(post=1).distinct()

    return {"feeds_list": feeds_list, "tag": tag}


@register.inclusion_tag("tags/blocks/related_list.html")
def related_tags_for(tag, count=20):
    related_tags = Tag.objects.none()

    max_posts_count = related_tags and related_tags[0].post__count or 0

    return {"related_tags": related_tags, "max_posts_count": max_posts_count}


@register.simple_tag
def tags_count_for(instance):
    if isinstance(instance, Feed):
        return Tag.objects.filter(post__feed=instance
            ).distinct().count()
    elif isinstance(instance, Author):
        return Tag.objects.filter(post__feed__author=instance
            ).distinct().count()
    else:
        return 0


@register.inclusion_tag("feeds/blocks/related_feeds.html")
def related_feeds_for(feed, count=10):
    feed_tags = Tag.objects.none() #filter(post__feed=feed).distinct()

    related_feeds = []
    if feed_tags:
        related_feeds = Feed.objects.filter(post__tags__in=feed_tags
            ).exclude(pk=feed.pk).distinct()[:count]

    return {"related_feeds": related_feeds}


@register.inclusion_tag("posts/details.html")
def post_details(post):
    return {"post": post}
    
#@register.simple_tag
#def year_cloud_for(instance):
    #if isinstance(instance, Feed):
        #return Post.objects.values("date_modified").distinct().annotate(Count("pk")).order_by("date_modified")
    #elif isinstance(instance, Author):
        #return []
    #else:
        #return []