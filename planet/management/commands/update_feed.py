#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from planet.management.commands import process_feed

import logging
class Command(BaseCommand):
    help = "Update a feed."
    args = "<feed_url>"

    def handle(self, *args, **options):
        plogger = logging.getLogger('PlanetLogger')
        plogger.info("Update Feed")

        if not len(args):
            plogger.error("You must provide the feed url as parameter")
            exit(0)

        feed_url = args[0]
        # process feed in create-mode
        process_feed(feed_url, create=False)
                