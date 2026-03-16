import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from readability import Document

from planet.models import Author, Blog, Feed, Post
from planet.settings import PLANET_CONFIG

register = template.Library()


@register.filter
@stringfilter
def clean_html(html):
    if not html:
        return ""
    return mark_safe(Document(html).summary(html_partial=True))


@register.simple_tag
def get_first_paragraph(body):
    if body is None:
        return ""

    cleaned_text = strip_tags(body)
    cleaned_text = re.sub("\\s+", " ", cleaned_text)
    split = [t for t in cleaned_text.split(".") if len(t) > 80]
    return split and split[0] or cleaned_text[:80]


@register.simple_tag
def get_authors_for_blog(blog):
    return Author.objects.for_blog(blog)


@register.simple_tag
def blogs_for_author(author):
    return Blog.objects.for_author(author)


@register.inclusion_tag("planet/authors/blocks/list_for_feed.html")
def authors_for_feed(feed):
    return {"author_list": Author.objects.for_feed(feed)}


@register.inclusion_tag("planet/feeds/blocks/list_for_author.html")
def feeds_for_author(author):
    return {"feed_list": Feed.objects.for_author(author)}


@register.inclusion_tag("planet/posts/blocks/list.html")
def recent_posts():
    post_list = Post.objects.all()[: PLANET_CONFIG["RECENT_POSTS_LIMIT"]]
    return {"post_list": post_list}


@register.inclusion_tag("planet/blogs/blocks/list.html")
def recent_blogs():
    blog_list = Blog.objects.order_by("-date_created")[: PLANET_CONFIG["RECENT_BLOGS_LIMIT"]]
    return {"blog_list": blog_list}


@register.simple_tag
def post_titles(posts, limit=5):
    """Return a comma-separated string of post titles."""
    titles = list(posts.values_list("title", flat=True)[:limit])
    return ", ".join(titles)
