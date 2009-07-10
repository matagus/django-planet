#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from django import template
from django.db.models import Count, Max, F
from django.conf import settings

from planet.models import Tag, Subscriber, Feed

register = template.Library()

@register.simple_tag
def normalize_number(number, max_values, levels=16):
    return 14 + ((float(number) / float(max_values)) * levels)

@register.inclusion_tag('tags/blocks/cloud.html')
def tags_cloud(min_posts_count=1):
    max_posts = Tag.objects.annotate(count=Count("post"))

    max_posts = max_posts.filter(
        count__gt=min_posts_count, name__isnull=False)

    max_posts = max_posts.aggregate(Max("count"))
    
    max_posts_count = max_posts["count__max"]

    tags_cloud = Tag.objects.annotate(count=Count("post"))

    tags_cloud = tags_cloud.filter(name__isnull=False,
        count__gt=min_posts_count).order_by("name")

    return {"tags_cloud": tags_cloud, "max_posts_count": max_posts_count}

@register.inclusion_tag('tags/blocks/subscribers_cloud.html')
def tags_cloud_for_subscriber(subscriber=None, min_posts_count=0):
    max_posts = Tag.objects.annotate(count=Count("post"))

    max_posts = max_posts.filter(name__isnull=False,
        count__gt=min_posts_count, post__feed__subscriber=subscriber)

    max_posts = max_posts.aggregate(Max("count"))
    
    max_posts_count = max_posts["count__max"]

    tags_cloud = Tag.objects.annotate(count=Count("post"))

    tags_cloud = tags_cloud.filter(name__isnull=False,
        count__gt=min_posts_count, post__feed__subscriber=subscriber
        ).order_by("name")

    return {"subscriber": subscriber, "tags_cloud": tags_cloud,
        "max_posts_count": max_posts_count}

@register.inclusion_tag('tags/blocks/feeds_cloud.html')
def tags_cloud_for_feed(feed=None, min_posts_count=0):
    max_posts = Tag.objects.annotate(count=Count("post"))

    max_posts = max_posts.filter(name__isnull=False,
        count__gt=min_posts_count, post__feed=feed)

    max_posts = max_posts.aggregate(Max("count"))
    
    max_posts_count = max_posts["count__max"]

    tags_cloud = Tag.objects.annotate(count=Count("post"))

    tags_cloud = tags_cloud.filter(name__isnull=False,
        count__gt=min_posts_count, post__feed=feed
        ).order_by("name")

    return {"feed": feed, "tags_cloud": tags_cloud,
        "max_posts_count": max_posts_count}

@register.inclusion_tag('subscribers/blocks/list_for_tag.html')
def subscribers_about(tag):
    subscribers = Subscriber.objects.filter(site=settings.FEEDJACK_SITE_ID,
        feed__post__tags__name=tag).distinct()

    return {"subscribers": subscribers, "tag": tag}

@register.inclusion_tag('feeds/blocks/list_for_tag.html')
def feeds_about(tag):
    feeds_list = Feed.objects.filter(
        subscriber__site=settings.FEEDJACK_SITE_ID,
        post__tags__name=tag).distinct()

    return {"feeds_list": feeds_list, "tag": tag}

@register.inclusion_tag("tags/blocks/related_list.html")
def related_tags_for(tag, count=20):
    related_tags = Tag.objects.filter(post__tags=tag)\
        .annotate(Count("post")).exclude(name=tag.name)\
        .distinct().order_by("-post__count", "name")[:count]

    max_posts_count = related_tags and related_tags[0].post__count or 0

    return {"related_tags": related_tags, "max_posts_count": max_posts_count}

@register.simple_tag
def tags_count_for(instance):
    if isinstance(instance, Feed):
        return Tag.objects.filter(post__feed=instance
            ).distinct().count()
    elif isinstance(instance, Subscriber):
        return Tag.objects.filter(post__feed__subscriber=instance
            ).distinct().count()
    else:
        return 0

@register.inclusion_tag("feeds/blocks/related_feeds.html")
def related_feeds_for(feed, count=10):
    feed_tags = Tag.objects.filter(post__feed=feed
        ).distinct()

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
    #elif isinstance(instance, Subscriber):
        #return []
    #else:
        #return []