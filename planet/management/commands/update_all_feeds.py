#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.core.management.base import BaseCommand

from planet.management.commands import process_feed
from planet.models import Feed
from planet.signals import feeds_updated


class Command(BaseCommand):
    """
    Command to add a complete blog feed to our db.

    Usage:

    ./manage.py add_feed <feed_url>
    """
    def handle(self, *args, **options):
        new_posts_count = 0
        start = datetime.now()
        for feed_url in Feed.site_objects.all().values_list("url", flat=True):
            # process feed in create-mode
            new_posts_count += process_feed(feed_url, create=False)
        delta = datetime.now() - start
        print "Added %s posts in %d seconds" % (new_posts_count, delta.seconds)
        feeds_updated.send(sender=self, instance=self)

