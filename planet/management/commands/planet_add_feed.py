#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from planet.tasks import process_feed


class Command(BaseCommand):
    help = "Add a complete blog feed to our db."
    args = "<feed_url>"
    option_list = BaseCommand.option_list + (
        make_option('-c', '--category',
            action='store',
            dest='category',
            default=None,
            metavar='Title',
            help='Add this feed to a Category'),
        )

    def handle(self, *args, **options):
        if not len(args):
            self.stderr.write("You must provide the feed url as parameter")
            exit(0)

        feed_url = args[0]
        # process feed in create-mode
        process_feed.delay(feed_url, create=True, category_title=options['category'])
        self.stdout.write("Feed created. Posts scheduled to be retrived soon.")
