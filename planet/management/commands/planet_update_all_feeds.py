import logging
import time

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from planet.backends import get_post_filter_backend
from planet.models import Feed, Post
from planet.settings import PLANET_CONFIG
from planet.utils import fetch_post_content, parse_feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Update all active feeds")

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        post_filter = get_post_filter_backend()
        total = Feed.objects.active().count()
        logger.info("Starting feed update: %d active feeds.", total)
        if verbosity >= 2:
            self.stdout.write(f"Starting feed update: {total} active feeds.")

        feeds_checked = 0
        total_posts = 0
        errors = 0

        for feed in Feed.objects.active().iterator():
            try:
                feed_data = parse_feed(feed.url, etag=feed.etag, modified=feed.last_modified)
            except Exception as exc:
                logger.error("Error fetching feed %s: %s", feed.url, exc)
                self.stderr.write(self.style.ERROR(f"Feed #{feed.pk}: fetch failed; see application log."))
                errors += 1
                continue

            if getattr(feed_data, "status", None) == 304:
                logger.info("Feed %s not modified (304), skipping.", feed.url)
                if verbosity >= 2:
                    self.stdout.write(f"Feed #{feed.pk} not modified (304).")
                feed.mark_checked()
                feeds_checked += 1
                continue

            if feed_data.bozo and not feed_data.entries:
                logger.warning("Feed %s returned bozo error: %s", feed.url, feed_data.bozo_exception)
                self.stderr.write(
                    self.style.ERROR(f"Feed #{feed.pk}: could not parse the empty feed; see application log.")
                )
                errors += 1
                continue

            new_posts = 0
            created_posts = []
            with transaction.atomic():
                if feed.last_checked is None:
                    feed.update_metadata(feed_data)
                    feed.blog.update_metadata(feed_data)

                entries = post_filter.filter_entries(feed_data.entries, feed)
                for entry in entries:
                    entry_url = entry.get("link") or ""
                    if not entry_url:
                        logger.debug("Skipping entry with no URL in feed %s: title=%r", feed.url, entry.get("title"))
                        continue

                    try:
                        Post.objects.get_by_url(entry_url)
                    except Post.DoesNotExist:
                        post = Post.objects.create_with_authors(entry, feed)
                        if post is not None:
                            logger.debug("New post: %r (feed=%s)", entry.get("title"), feed.url)
                            new_posts += 1
                            created_posts.append(post)

                feed.mark_checked(feed_data)

            if PLANET_CONFIG["FETCH_ORIGINAL_CONTENT"]:
                for post in created_posts:
                    post.original_content = fetch_post_content(post.url)
                    post.save(update_fields=["original_content"])
                    if delay := PLANET_CONFIG["FETCH_CONTENT_DELAY"]:
                        time.sleep(delay)

            feeds_checked += 1
            total_posts += new_posts
            if verbosity >= 2:
                self.stdout.write(f"Feed #{feed.pk}: {new_posts} new post(s).")
            if new_posts > 0:
                logger.info("Feed %s: %d new post(s).", feed.url, new_posts)
            else:
                logger.debug("Feed %s: no new posts.", feed.url)

        logger.info(
            "Feed update complete: %d feeds checked, %d new posts, %d errors.", feeds_checked, total_posts, errors
        )
        if verbosity >= 1:
            summary = f"Feed update complete: {feeds_checked} feeds checked, {total_posts} new posts, {errors} errors."
            self.stdout.write(self.style.WARNING(summary) if errors else self.style.SUCCESS(summary))
