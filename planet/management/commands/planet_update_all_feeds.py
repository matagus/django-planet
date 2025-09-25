from django.utils import timezone
from django.core.management.base import BaseCommand

from planet.models import Author, PostAuthorData, Feed, Post
from planet.utils import parse_feed


class Command(BaseCommand):
    help = "Update all active feeds"

    def handle(self, *args, **options):
        # FIXME: Feed.active_objects --> implement!
        for feed in Feed.objects.iterator():
            try:
                feed_data = parse_feed(feed.url)
            except Exception:
                # FIXME: use the right exception
                continue

            for entry in feed_data.entries:
                try:
                    post = Post.objects.get_by_url(entry.link)
                except Post.DoesNotExist:
                    # Create the db rows needed: Post, PostAuthorData and Author
                    post = Post.objects.create_from(entry, feed)

                    # Some feeds doesn't have authors information
                    for author_dict in entry.get("authors", []):
                        # FIXME: move this logic to a custom Author's create method, do validations there!
                        try:
                            name = author_dict["name"].strip()
                        except Exception:
                            continue

                        if name:
                            author, created = Author.objects.get_or_create(name=name)
                            PostAuthorData.objects.create(post=post, author=author)

            feed.last_checked = timezone.now()
            feed.etag = feed_data.get("etag")
            feed.save()
