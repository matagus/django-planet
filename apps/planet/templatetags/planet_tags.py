#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from django import template
from django.db.models import Count, Max, F

from planet.models import Author, Feed, Blog, Post

from tagging.models import Tag, TaggedItem


register = template.Library()


@register.inclusion_tag('authors/blocks/list_for_tag.html')
def authors_about(tag):
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    authors = Author.site_objects.filter(post__in=post_ids).distinct()

    return {"authors": authors, "tag": tag}


@register.inclusion_tag('feeds/blocks/list_for_tag.html')
def feeds_about(tag):
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    feeds_list = Feed.site_objects.filter(post__in=post_ids).distinct()

    return {"feeds_list": feeds_list, "tag": tag}


@register.inclusion_tag("tags/blocks/related_list.html")
def related_tags_for(tag, count=20):
    related_tags = Tag.objects.none()

    max_posts_count = related_tags and related_tags[0].post__count or 0

    return {"related_tags": related_tags, "max_posts_count": max_posts_count}

@register.inclusion_tag("posts/details.html")
def post_details(post):
    return {"post": post}

@register.inclusion_tag("posts/full_details.html")
def post_full_details(post):
    return {"post": post}
    
#@register.simple_tag
#def year_cloud_for(instance):
    #if isinstance(instance, Feed):
        #return Post.objects.values("date_modified").distinct().annotate(Count("pk")).order_by("date_modified")
    #elif isinstance(instance, Author):
        #return []
    #else:
        #return []