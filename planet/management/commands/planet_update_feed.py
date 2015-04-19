#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from planet.tasks import process_feed


class Command(BaseCommand):
    help = "Update a feed."
    args = "<feed_url>"

    def handle(self, *args, **options):
        if not len(args):
            print("You must provide the feed url as parameter")
            exit(0)

        feed_url = args[0]
        # process feed in create-mode
        process_feed.delay(feed_url, create=False)
