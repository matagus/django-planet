import logging
import time

from django.core.management.base import CommandError, LabelCommand
from django.db import transaction

from planet.backends import get_post_filter_backend
from planet.models import Blog, Feed, Post
from planet.settings import PLANET_CONFIG
from planet.utils import fetch_post_content, parse_feed

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
            created_posts = []
            with transaction.atomic():
                feed = Feed.objects.create_from(feed_data, blog=blog)
                post_filter = get_post_filter_backend()
                entries = post_filter.filter_entries(feed_data.entries, feed)
                for entry in entries:
                    post = Post.objects.create_with_authors(entry, feed)
                    if post is not None:
                        created_posts.append(post)

            if PLANET_CONFIG["FETCH_ORIGINAL_CONTENT"]:
                for post in created_posts:
                    post.original_content = fetch_post_content(post.url)
                    post.save(update_fields=["original_content"])
                    if delay := PLANET_CONFIG["FETCH_CONTENT_DELAY"]:
                        time.sleep(delay)

            logger.info("Feed %s created with %d posts.", feed.url, len(created_posts))
            self.stdout.write(f"Feed for url={feed.url} was successfully created!")
