import logging

from django.core.management.base import CommandError, LabelCommand
from django.db import transaction

from planet.backends import get_post_filter_backend
from planet.models import Blog, Feed, Post
from planet.utils import parse_feed

logger = logging.getLogger(__name__)


class Command(LabelCommand):
    help = "Add a new feed to the database"
    label = "url"

    def handle_label(self, label, **options):
        feed_url = label
        logger.info("Adding feed: %s", feed_url)

        try:
            feed_data = parse_feed(feed_url)
        except Exception as e:
            raise CommandError(f"Error retrieving feed {feed_url}: {e}")

        blog, created = Blog.objects.get_or_create_from_feed(feed_data)
        logger.info("Blog %r (created=%s)", blog, created)

        try:
            feed = Feed.objects.get_by_url(feed_url)
            logger.warning("Feed already exists: %s", feed_url)
            self.stdout.write(f"Feed for url={feed.url} already exists!")
        except Feed.DoesNotExist:
            with transaction.atomic():
                feed = Feed.objects.create_from(feed_data, blog=blog)
                post_filter = get_post_filter_backend()
                entries = post_filter.filter_entries(feed_data.entries, feed)
                post_count = 0
                for entry in entries:
                    post = Post.objects.create_with_authors(entry, feed)
                    if post is not None:
                        post_count += 1
            logger.info("Feed %s created with %d posts.", feed.url, post_count)
            self.stdout.write(f"Feed for url={feed.url} was successfully created!")
