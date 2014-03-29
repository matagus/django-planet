# -*- coding: utf-8 -*-
"""
Several useful template tags!
"""

import re

from django import template
from django.template import TemplateSyntaxError, Node, loader, Variable
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import smart_split
from django.utils.translation import ugettext as _

from planet.models import Author, Feed, Blog, Post
from planet.settings import PLANET_CONFIG

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
def related_tags_for(tag, count=PLANET_CONFIG["RELATED_TAGS_MIN_COUNT"]):
    """
    Displays a list of tags that have been used for tagging Posts instances
    always that <tag> have been used too.
    """
    related_tags = Tag.objects.related_for_model([tag], Post, counts=True)

    return {"related_tags": related_tags[:count]}


@register.inclusion_tag("planet/dummy.html")
def post_details(post, template="planet/posts/details.html"):
    """
    Displays info about a post: title, date, feed and tags.
    """
    return {"template": template, "post": post}


@register.inclusion_tag("planet/posts/full_details.html")
def post_full_details(post):
    """
    Displays full info about a post: title, date, feed, authors and tags,
    and it also displays external links to post and blog.
    """
    return {"post": post}


@register.inclusion_tag("planet/tags/blocks/feeds_cloud.html")
def cloud_for_feed(feed, min_count=PLANET_CONFIG["FEED_TAG_CLOUD_MIN_COUNT"]):
    """
i    Displays a tag cloud for a given feed object.
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"feed": feed}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "feed": feed}


@register.inclusion_tag("planet/tags/blocks/authors_cloud.html")
def cloud_for_author(author, min_count=PLANET_CONFIG["AUTHOR_TAG_CLOUD_MIN_COUNT"]):
    """
    Displays a tag cloud for a given author object.
    """
    tags_cloud = Tag.objects.cloud_for_model(
        Post, filters={"authors": author}, min_count=min_count)

    return {"tags_cloud": tags_cloud, "author": author}


@register.inclusion_tag("planet/tags/blocks/blogs_cloud.html")
def cloud_for_blog(blog, min_count=PLANET_CONFIG["BLOG_TAG_CLOUD_MIN_COUNT"]):
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
    def __init__(self, limit=None, tag=None, category=None, template=None):
        self.limit = limit
        self.tag = tag
        self.category = category
        self.template = template

    def resolve(self, context, vars):
        """
        Resolve all the template variables listed in vars through the given
        context
        """
        for var in vars:
            val_var = self.__getattribute__(var)
            if val_var is not None:
                self.__setattr__(var, Variable(val_var).resolve(context))

    def process(self, context):
        self.resolve(context, ('tag', 'category', 'template', 'limit'))
        if self.tag is not None:
            posts = TaggedItem.objects.get_by_model(
                Post.site_objects, self.tag)
        else:
            posts = Post.site_objects

        #select also related objects, in this way we avoid future queries to
        #retrieve for example the blog name
        posts = posts.select_related()

        if self.category is not None:
            posts = posts.filter(feed__category__title=self.category)

        ##TODO: test under mysql and sqlite
        posts = posts.extra(
            select={'date': "COALESCE(planet_post.date_modified, planet_post.date_created)"}
        ).order_by('-date')

        if self.limit is not None:
            posts = posts[:self.limit]

        context['posts'] = posts

        if self.template is None:
            self.template = "planet/list.html"

        return (self.template, context)

    def render(self, context):
        template, context = self.process(context)
        return loader.get_template(template).render(context)


@register.tag()
def planet_post_list(parser, token):
    """
    Render a list of posts using the planet/list.html template.

    Params:
        limit: limit to this number of entries
        tag: select only Posts that matches this tag
        category: select only Posts that belongs to Feeds under this Category
        template: render using a different template

    Examples:
        {% planet_post_list with limit=10 tag=tag %}
        {% planet_post_list with tag="Redis" %}
        {% planet_post_list with category="PyPy" %}
    """
    bits = list(smart_split(token.contents))
    len_bits = len(bits)
    kwargs = {}
    if len_bits > 1:
        if bits[1] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(2, len_bits):
            try:
                name, value = bits[i].split('=')
                if name in ('tag', 'category', 'template', 'limit'):
                    kwargs[str(name)] = value
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


@register.assignment_tag
def get_first_paragraph(body):
    if body is None:
        return ""

    cleaned_text = strip_tags(body)
    cleaned_text = re.sub("\s+", " ", cleaned_text)
    splitted = [t for t in cleaned_text.split(".") if len(t) > 80]
    return splitted and splitted[0] or cleaned_text[:80]


@register.filter
def post_count(obj):
    if isinstance(obj, Author):
        return Post.objects.filter(authors=obj).count()
    elif isinstance(obj, Blog):
        return Post.objects.filter(feed__blog=obj).distinct().count()
    else:
        return 0


@register.filter
def get_authors(blog):
    return Author.objects.filter(post__feed__blog=blog).distinct()


@register.filter
def get_blogs(author):
    return Blog.objects.filter(feed__post__authors=author).distinct()


@register.assignment_tag
def latest_posts(count=10):
    """
    A way to get latest posts from inside a template
    """
    return Post.objects.all()[:count]
