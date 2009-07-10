#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser

from django.core.management.base import BaseCommand
from django.conf import settings

from feedjack.models import Feed, Subscriber


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not len(args):
            print "You must provide the feed url as parameter"
            exit(0)

        url = args[0]

        document = feedparser.parse(url)
        try:
            title = document.feed.title
        except AttributeError:
            title = "--"
        
        try:
            author_name = document.feed.author_detail.name
            if not author_name:
                author_name = document.feed.author
        except AttributeError:
            author_name = None

        try:
            feed = Feed(feed_url=url, name=title)
            feed.save()
        except:
            print "That feed is already saved."
            exit(0)

        subscriber = Subscriber()
        subscriber.site_id = settings.SITE_ID
        subscriber.feed = feed
        subscriber.name = author_name
        subscriber.save()
        print "done"