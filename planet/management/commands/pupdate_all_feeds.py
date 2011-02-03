#!/usr/bin/env python
# -*- coding: utf-8 -*-
import eventlet
eventlet.monkey_patch(socket=True)
from datetime import datetime
from django.core.management.base import NoArgsCommand

from planet.management.commands import process_feed
from planet.models import Feed
from planet.signals import feeds_updated



class Command(NoArgsCommand):
    help = "Update all feeds"

    
    def handle(self, *args, **options):
        new_posts_count = 0
        start = datetime.now()

        feed_urls = Feed.site_objects.all().values_list("url", flat=True)
        pool = eventlet.GreenPool()
        for result in pool.imap(process_feed, feed_urls):
            new_posts_count += result
        
        delta = datetime.now() - start
        print "Added %s posts in %d seconds" % (new_posts_count, delta.seconds)
        feeds_updated.send(sender=self, instance=self)

