import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from planet.backends import get_post_filter_backend
from planet.models import Feed, Post
from planet.utils import parse_feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update all active feeds"

    def handle(self, *args, **options):
        post_filter = get_post_filter_backend()
        for feed in Feed.objects.active().iterator():
            try:
                feed_data = parse_feed(feed.url, etag=feed.etag, modified=feed.last_modified)
            except Exception as exc:
                logger.error("Error fetching feed %s: %s", feed.url, exc)
                continue

            if getattr(feed_data, "status", None) == 304:
                logger.info("Feed %s not modified (304), skipping.", feed.url)
                feed.mark_checked()
                continue

            if feed_data.bozo and not feed_data.entries:
                logger.warning("Feed %s returned bozo error: %s", feed.url, feed_data.bozo_exception)
                continue

            with transaction.atomic():
                entries = post_filter.filter_entries(feed_data.entries, feed)
                for entry in entries:
                    try:
                        Post.objects.get_by_url(entry.link)
                    except Post.DoesNotExist:
                        Post.objects.create_with_authors(entry, feed)

                feed.mark_checked(feed_data)
