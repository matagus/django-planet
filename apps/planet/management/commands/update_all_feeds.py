#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        for feed_url in Feed.site_objects.all().values_list("url", flat=True):
            # process feed in create-mode
            process_feed(feed_url, create=False)
        feeds_updated.send(sender=self, instance=self)
                