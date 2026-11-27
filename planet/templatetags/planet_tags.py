import re

from django import template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from planet.models import Author, Blog, Feed, Post
from planet.settings import PLANET_CONFIG

register = template.Library()


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


@register.simple_tag
def attr(obj, name):
    """Resolve an attribute by name, e.g. {% attr item "title" as label %}.

    Used by planet/blocks/nav_list.html so the sidebar link text is a
    presentation decision instead of a UI property on the models. Methods
    are called if they take no arguments; missing attributes yield "".
    Output is auto-escaped like any other template variable.
    """
    try:
        value = getattr(obj, name)
    except Exception:
        return ""
    return value() if callable(value) else value


def _nav_list_context(items, title, label_field, nav_class=""):
    """Context for the shared planet/blocks/nav_list.html sidebar partial."""
    return {"items": items, "title": title, "label_field": label_field, "nav_class": nav_class}


@register.inclusion_tag("planet/blocks/nav_list.html")
def authors_for_feed(feed):
    return _nav_list_context(Author.objects.for_feed(feed), _("Authors for this feed"), "name", "mt-3")


@register.inclusion_tag("planet/blocks/nav_list.html")
def feeds_for_author(author):
    return _nav_list_context(Feed.objects.for_author(author), _("Feeds"), "title", "mt-3")


@register.inclusion_tag("planet/blocks/nav_list.html")
def recent_posts():
    post_list = Post.objects.all()[: PLANET_CONFIG["RECENT_POSTS_LIMIT"]]
    return _nav_list_context(post_list, _("Recent Posts"), "title")


@register.inclusion_tag("planet/blocks/nav_list.html")
def recent_blogs():
    blog_list = Blog.objects.published().order_by("-date_created")[: PLANET_CONFIG["RECENT_BLOGS_LIMIT"]]
    return _nav_list_context(blog_list, _("Recently Added Blogs"), "title", "mb-3")


@register.simple_tag
def post_titles(posts, limit=5):
    """Return a comma-separated string of post titles."""
    titles = list(posts.values_list("title", flat=True)[:limit])
    return ", ".join(titles)
