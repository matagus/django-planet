#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Several useful template tags!
"""

import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.template import TemplateSyntaxError, Node, loader
from django.utils.translation import ugettext as _

from planet.models import Author, Feed, Blog, Post

from tagging.models import Tag, TaggedItem


register = template.Library()


@register.inclusion_tag('planet/authors/blocks/list_for_tag.html')
def authors_about(tag):
    """
    Displays a list of authors who have been written a post tagged with this tag.    
    """
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    authors = Author.site_objects.filter(post__in=post_ids).distinct()

    return {"authors": authors, "tag": tag}


@register.inclusion_tag('planet/feeds/blocks/list_for_tag.html')
def feeds_about(tag):
    """
    Displays a list of feeds whose posts have been tagged with this tag.
    """
    post_ids = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).values_list("id", flat=True)
    
    feeds_list = Feed.site_objects.filter(post__in=post_ids).distinct()

    return {"feeds_list": feeds_list, "tag": tag}


@register.inclusion_tag("planet/tags/blocks/related_list.html")
def related_tags_for(tag, count=20):
    """
    Displays a list of tags that have been used for tagging Posts instances
    always that <tag> have been used too.
    """
    related_tags = Tag.objects.related_for_model([tag], Post, counts=True)

    return {"related_tags": related_tags[:count]}


@register.inclusion_tag("planet/posts/details.html")
def post_details(post):
    """
    Displays info about a post: title, date, feed and tags.
    """
    return {"post": post}


@register.inclusion_tag("planet/posts/full_details.html")
def post_full_details(post):
    """
    Displays full info about a post: title, date, feed, authors and tags,
    and it also displays external links to post and blog.
    """
    return {"post": post}


@register.inclusion_tag("planet/tags/blocks/feeds_cloud.html")
def cloud_for_feed(feed, min_count=3):
    """
    Displays a tag cloud for a given feed object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"feed": feed}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "feed": feed}


@register.inclusion_tag("planet/tags/blocks/authors_cloud.html")
def cloud_for_author(author, min_count=3):
    """
    Displays a tag cloud for a given author object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"authors": author}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "author": author}


@register.inclusion_tag("planet/tags/blocks/blogs_cloud.html")
def cloud_for_blog(blog, min_count=3):
    """
    Displays a tag cloud for a given blog object.    
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"feed__blog": blog}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "blog": blog}


@register.inclusion_tag("planet/authors/blocks/list_for_feed.html")
def authors_for_feed(feed):

    authors = Author.site_objects.filter(post__feed=feed)

    return {"authors": authors, "feed": feed}


@register.inclusion_tag("planet/feeds/blocks/list_for_author.html")
def feeds_for_author(author):
    
    feeds = Feed.site_objects.filter(
        post__authors=author).order_by("title").distinct()

    return {"feeds_list": feeds, "author": author}


class PlanetPostList(Node):
    def __init__(self, limit=None, tag=None):
        self.limit = limit
        self.tag = tag

    def render(self, context):
        if self.tag is not None:
            try:
                tag_name = context[self.tag]
            except KeyError:
                raise TemplateSyntaxError(_("%s: no variable %s in context") % (bits[0], tag_name))
            posts = TaggedItem.objects.get_by_model(
                Post.site_objects, tag_name).order_by("-date_modified")
        else:
            posts = Post.site_objects.all().order_by("-date_modified")

        if self.limit is not None:
            posts = posts[:self.limit]

        context['posts'] = posts
        return loader.get_template("planet/list.html").render(context)


@register.tag()
def planet_post_list(parser, token):
    """
    Render a list of posts using the planet/list.html template.

    Params:
        limit: limit to this number of entries
        tag: select only Posts that matches this tag. This must be the name of a context variable, not a string.

    Example:
        {% planet_post_list with limit=10 tag=tag %}
    """
    bits = token.contents.split()
    len_bits = len(bits)
    kwargs = {}
    if len_bits > 1:
        if bits[1] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(2, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'limit':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                elif name == 'tag':
                    try:
                        kwargs[str(name)] = value
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })

    return PlanetPostList(**kwargs)


@register.filter
@stringfilter
def clean_html(html):
    pattern_list = ('(style=".*?")', '(<style.*?</style>")',
        '(<script.*?</script>")', )
    for pattern in pattern_list:
        html = re.sub(pattern, '', html)

    pattern_list = (('(<br.?/>){3,}', '<br/><br/>'), )
    for (pattern, replacement) in pattern_list:
        html = re.sub(pattern, replacement, html)
    return mark_safe(html)