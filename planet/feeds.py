# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaks, escape
from django.utils.translation import ugettext_lazy as _

from planet.models import Post, Author

from tagging.models import Tag, TaggedItem


ITEMS_PER_FEED = getattr(settings, 'PLANET_ITEMS_PER_FEED', 50)

class PostFeed(Feed):

    def __init__(self, *args, **kwargs):
        super(PostFeed, self).__init__(*args, **kwargs)
        self.site = Site.objects.get_current()

    def title(self):
        return _(u"%s latest posts") % (self.site.name, )

    def link(self):
        return reverse("planet_rss_feed")

    def items(self):
        return Post.objects.order_by('-date_modified')

    def item_title(self, post):
        return post.title

    def item_description(self, post):
        return post.content

    def item_id(self, post):
        return post.guid

    def item_updated(self, post):
        return post.date_modified

    def item_published(self, post):
        return post.date_created

    def item_content(self, post):
        return {"type" : "html", }, linebreaks(escape(post.content))

    def item_links(self, post):
        return [{"href" : reverse("planet_post_detail", args=(post.pk, post.get_slug()))}]

    def item_authors(self, post):
        return [{"name" : post.author}]


class AuthorFeed(PostFeed):

    def get_object(self, request, author_id):
        return get_object_or_404(Author, pk=author_id)

    def title(self, author):
        return _("Posts by %(author_name)s - %(site_name)s") %\
            {'author_name': author.name, 'site_name': self.site.name}

    def links(self, author):
        return ({'href': reverse("planet_author_show", args=(author.pk, author.get_slug()))},)

    def items(self, author):
        return Post.objects.filter(authors=author,
            ).distinct().order_by("-date_created")[:ITEMS_PER_FEED]


class TagFeed(PostFeed):

    def get_object(self, request, tag):
        return get_object_or_404(Tag, name=tag)

    def title(self, tag):
        return _("Posts under %(tag)s tag - %(site_name)s") %\
            {'tag': tag, 'site_name': self.site.name}

    def links(self, tag):
        return ({'href': reverse("planet_tag_detail", kwargs={"tag": tag.name})},)

    def items(self, tag):
        return TaggedItem.objects.get_by_model(
            Post.objects.filter(feed__site=self.site), tag)\
            .distinct().order_by("-date_created")[:ITEMS_PER_FEED]


class AuthorTagFeed(PostFeed):

    def get_object(self, request, author_id, tag):
        self.tag = tag
        return get_object_or_404(Author, pk=author_id)

    def title(self, author):
        return _("Posts by %(author_name)s under %(tag)s tag - %(site_name)s")\
            % {'author_name': author.name, 'tag': self.tag, 'site_name': self.site.name}

    def links(self, author):
        return ({'href': reverse("planet_by_tag_author_show", args=(author.pk, self.tag))},)

    def items(self, author):
        return TaggedItem.objects.get_by_model(
            Post.objects.filter(feed__site=self.site, authors=author), self.tag)\
            .distinct().order_by("-date_created")[:ITEMS_PER_FEED]
