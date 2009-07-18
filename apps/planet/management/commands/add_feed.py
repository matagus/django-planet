#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
from datetime import datetime
import time

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site

from planet.models import (Blog, Generator, Feed, FeedLink, Post, PostLink,
        Author, PostAuthorData, Enclosure)


USER_AGENT = "Mozilla/5.0 (X11;U; Linux i686; es-AR; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5"

class Command(BaseCommand):
    """
    Command to add a complete blog feed to our db.

    Usage:

    ./manage.py add_feed <feed_url>
    """
    def handle(self, *args, **options):
        if not len(args):
            print "You must provide the feed url as parameter"
            exit(0)

        feed_url = str(args[0]).strip()

        try:
            Feed.objects.get(url=feed_url)
            print "This feed already exists!"
        except Feed.DoesNotExist:
            # retrive and parse feed
            document = feedparser.parse(feed_url, agent=USER_AGENT)

            current_site = Site.objects.get(pk=settings.SITE_ID)
            
            title = document.feed.get("title", "--")
            subtitle = document.feed.get("subtitle")
            blog_url = document.feed.get("link")
            rights = document.feed.get("rights") or document.feed.get("license")
            info = document.feed.get("info")
            guid = document.feed.get("id")
            image_url = document.feed.get("image", {}).get("href")
            icon_url = document.feed.get("icon")
            language = document.feed.get("language")
            etag = document.get("etag", '')
            last_modified = document.get("updated_parsed", datetime.now())

            blog, created = Blog.objects.get_or_create(
                url=blog_url, defaults={"title": title})

            generator_dict = document.feed.get("generator_detail", {})
            if generator_dict:
                generator, created = Generator.objects.get_or_create(
                    name=generator_dict.get("name", "--"),
                    link=generator_dict.get("link"),
                    version=generator_dict.get("version"))
            else:
                generator = None

            planet_feed = Feed(title=title, subtitle=subtitle, blog=blog,
                url=feed_url, rights=rights, info=info, guid=guid,
                image_url=image_url, icon_url=icon_url, language=language,
                etag=etag, last_modified=last_modified, generator=generator,
                is_active=True, last_checked=datetime.now(),
                site=current_site
            )
            planet_feed.save()

            for tag_dict in document.feed.get("tags", []):
                name = tag_dict.get("term")
                if name:
                    print name
            
            for link_dict in document.feed.get("links", []):
                feed_link, created = FeedLink.objects.get_or_create(
                    feed=planet_feed,
                    rel=link_dict.get("rel"),
                    mime_type=link_dict.get("type"),
                    link=link_dict.get("href", blog_url)
                )

            # retrive and store feed posts
            entries = document.entries

            total_results = int(document.feed.get("opensearch_totalresults", 0))
            items_per_page = 25
            if total_results:
                while total_results > len(entries):
                    opensearch_url = "%s?start-index=%d&max-results=%d" %\
                        (feed_url, len(entries) + 1, items_per_page)

                    print "retriving %s..." % opensearch_url
                    document = feedparser.parse(opensearch_url, agent=USER_AGENT)
                    entries.extend(document.entries)
                    time.sleep(5)

            print "Processing %d entries" % len(entries)
            for entry in entries:
                title = entry.get("title", "")
                url = entry.get("link")
                guid = entry.get("guid")
                content = entry.get("content", [{"value": ""}])[0]["value"]
                comments_url = entry.get("comments")
                date_modified = entry.get("updated_parsed") or\
                    entry.get("published_parsed")
                try:
                    date_modified = datetime.fromtimestamp(
                        time.mktime(date_modified))
                except:
                    print "oops"
                    date_modified = None
                
                post = Post(title=title, url=url, guid=guid, content=content,
                    comments_url=comments_url, date_modified=date_modified,
                    feed=planet_feed)
                post.save()                

                # create post tags...
                post_tags = []
                for tag_dict in entry.get("tags", []):
                    tag_name = tag_dict.get("term") or tag_dict.get("label")
                    post_tags.append(tag_name)

                if post_tags:
                    post.tags = " ,".join(post_tags)

                # create post links...
                for link_dict in entry.get("links", []):
                    post_link, created = PostLink.objects.get_or_create(
                        post=post,
                        rel=link_dict.get("rel"),
                        mime_type=link_dict.get("type"),
                        link=link_dict.get("href", blog_url),
                        title=link_dict.get("title", "--")
                    )

                # create and store enclosures...
                for enclosure_dict in entry.get("enclosures", []):
                    post_enclosure, created = Enclosure.objects.get_or_create(
                        post=post,
                        length=enclosure_dict.get("length"),
                        mime_type=enclosure_dict.get("type"),
                        link=enclosure_dict.get("href")
                    )

                # create and store author...
                author_dict = entry.get("author_detail")
                if author_dict:
                    author, created = Author.objects.get_or_create(
                        name=author_dict.get("name", ""),
                        email=author_dict.get("email", ""),
                        profile_url=author_dict.get("href")
                    )
                    try:
                        PostAuthorData.objects.get(author=author, post=post)
                    except PostAuthorData.DoesNotExist:
                        pad = PostAuthorData(author=author, post=post)
                        pad.save()

                # create and store contributors...
                for contributor_dict in entry.get("contributors", []):
                    contributor, created = Author.objects.get_or_create(
                        name=author_dict.get("name", ""),
                        email=author_dict.get("email", ""),
                        profile_url=contributor_dict.get("href")
                    )
                    try:
                        PostAuthorData.objects.get(author=contributor, post=post)
                    except PostAuthorData.DoesNotExist:
                        pad = PostAuthorData(author=contributor, post=post,
                            is_contributor=True)
                        pad.save()
                