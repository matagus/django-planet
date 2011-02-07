#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey #the best thing to do is put this import in manage.py
monkey.patch_socket()
from gevent.pool import Group
from datetime import datetime
from django.core.management.base import NoArgsCommand

from planet.management.commands import process_feed
from planet.models import Feed
from planet.signals import feeds_updated

import logging

import socket
socket.setdefaulttimeout(20.)

class Command(NoArgsCommand):
    help = "Update all feeds using gevent!"

    
    def handle(self, *args, **options):
        plogger = logging.getLogger('PlanetLogger')
        plogger.info("Parallel Update All Feeds")
        new_posts_count = 0
        start = datetime.now()

        feed_urls = Feed.site_objects.all().values_list("url", flat=True)
        pool = Group()
        for result in pool.imap_unordered(process_feed, feed_urls):
            new_posts_count += result
        
        delta = datetime.now() - start
        plogger.info("Added %s posts in %d seconds" % (new_posts_count, delta.seconds))
        feeds_updated.send(sender=self, instance=self)

