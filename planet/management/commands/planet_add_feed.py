from django.core.management.base import CommandError, LabelCommand

from planet.management.commands._helpers import create_authors_for_post
from planet.models import Blog, Feed, Post
from planet.utils import parse_feed


class Command(LabelCommand):
    help = "Add a new feed to the database"
    label = "url"

    def handle_label(self, label, **options):
        feed_url = label

        try:
            feed_data = parse_feed(feed_url)
        except Exception as e:
            raise CommandError(f"Error retrieving feed {feed_url}: {e}")

        blog, created = Blog.objects.get_or_create(url=feed_data.feed.link, defaults={"title": feed_data.feed.title})

        try:
            feed = Feed.objects.get_by_url(feed_url)
            self.stdout.write(f"Feed for url={feed.url} already exists!")
        except Feed.DoesNotExist:
            feed = Feed.objects.create_from(feed_data, blog=blog)
            self.stdout.write(f"Feed for url={feed.url} was successfully created!")

            for entry in feed_data.entries:
                post = Post.objects.create_from(entry, feed)
                create_authors_for_post(post, entry.get("authors", []))
