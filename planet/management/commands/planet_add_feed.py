from django.core.management.base import CommandError, LabelCommand

from planet.models import Author, PostAuthorData, Blog, Feed, Post
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
