import logging

from django.utils import timezone
from django.core.management.base import BaseCommand

from planet.management.commands._helpers import create_authors_for_post
from planet.models import Feed, Post
from planet.utils import parse_feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update all active feeds"

    def handle(self, *args, **options):
        for feed in Feed.objects.filter(is_active=True).iterator():
            try:
                feed_data = parse_feed(feed.url, etag=feed.etag, modified=feed.last_modified)
            except Exception as exc:
                logger.error("Error fetching feed %s: %s", feed.url, exc)
                continue

            if getattr(feed_data, "status", None) == 304:
                logger.info("Feed %s not modified (304), skipping.", feed.url)
                feed.last_checked = timezone.now()
                feed.save(update_fields=["last_checked"])
                continue

            if feed_data.bozo and not feed_data.entries:
                logger.warning("Feed %s returned bozo error: %s", feed.url, feed_data.bozo_exception)
                continue

            for entry in feed_data.entries:
                try:
                    Post.objects.get_by_url(entry.link)
                except Post.DoesNotExist:
                    post = Post.objects.create_from(entry, feed)
                    create_authors_for_post(post, entry.get("authors", []))

            feed.last_checked = timezone.now()
            feed.etag = feed_data.get("etag")
            feed.save(update_fields=["last_checked", "etag"])
