#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Several usefull template tags!
"""

from django import template
from django.db.models import Count, Max, F

from planet.models import Author, Feed, Blog, Post

from tagging.models import Tag, TaggedItem


register = template.Library()


@register.inclusion_tag('authors/blocks/list_for_tag.html')
def authors_about(tag):
    """
    Displays a list of authors who have been written a post tagged with this tag.    
    """
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    authors = Author.site_objects.filter(post__in=post_ids).distinct()

    return {"authors": authors, "tag": tag}


@register.inclusion_tag('feeds/blocks/list_for_tag.html')
def feeds_about(tag):
    """
    Displays a list of feeds whose posts have been tagged with this tag.
    """
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    feeds_list = Feed.site_objects.filter(post__in=post_ids).distinct()

    return {"feeds_list": feeds_list, "tag": tag}


@register.inclusion_tag("tags/blocks/related_list.html")
def related_tags_for(tag, count=20):
    """
    Displays a list of tags that have been used for tagging Posts instances
    always that <tag> have been used too.
    """
    related_tags = Tag.objects.related_for_model([tag], Post, counts=True)

    return {"related_tags": related_tags[:count]}


@register.inclusion_tag("posts/details.html")
def post_details(post):
    """
    Displays info about a post: title, date, feed and tags.
    """
    return {"post": post}


@register.inclusion_tag("posts/full_details.html")
def post_full_details(post):
    """
    Displays full info about a post: title, date, feed, authors and tags,
    and it also displays external links to post and blog.
    """
    return {"post": post}


@register.inclusion_tag("tags/blocks/feeds_cloud.html")
def cloud_for_feed(feed, min_count=3):
    """
    Displays a tag cloud for a given feed object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"feed": feed}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "feed": feed}


@register.inclusion_tag("tags/blocks/authors_cloud.html")
def cloud_for_author(author, min_count=3):
    """
    Displays a tag cloud for a given author object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"authors": author}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "author": author}


@register.inclusion_tag("tags/blocks/blogs_cloud.html")
def cloud_for_blog(blog, min_count=3):
    """
    Displays a tag cloud for a given blog object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"feed__blog": blog}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "blog": blog}


@register.inclusion_tag("authors/blocks/list_for_feed.html")
def authors_for_feed(feed):

    authors = Author.site_objects.filter(post__feed=feed)

    return {"authors": authors, "feed": feed}


@register.inclusion_tag("feeds/blocks/list_for_author.html")
def feeds_for_author(author):
    
    feeds = Feed.site_objects.filter(
        post__authors=author).order_by("title").distinct()

    return {"feeds_list": feeds, "author": author}