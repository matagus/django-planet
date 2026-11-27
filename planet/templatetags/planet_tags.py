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
    """Resolve an attribute by name, trying each comma-separated candidate.

    Used by planet/blocks/nav_list.html to pick a display label without the
    models carrying UI-specific properties::

        {% attr item "display_name,title,name" as label %}

    Returns the first non-empty value, or an empty string. Output is escaped at
    render time like any other template variable, so nothing is marked safe.
    """
    for candidate in (c.strip() for c in name.split(",")):
        if not candidate:
            continue
        try:
            value = getattr(obj, candidate)
        except Exception:
            continue
        if callable(value):
            value = value()
        if value:
            return value
    return ""


def _nav_list_context(items, title, label_field, nav_class=""):
    """Context for the shared planet/blocks/nav_list.html sidebar partial.

    ``label_field`` names the attribute each item exposes as its link text. It is
    resolved in the template, so which field a sidebar label comes from stays a
    presentation decision here rather than a property on the models. Pass a
    comma-separated list of fallbacks to tolerate custom model subclasses.
    """
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
