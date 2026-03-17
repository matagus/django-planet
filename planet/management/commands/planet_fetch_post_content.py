import logging
import time

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _t
from django.utils.translation import gettext_lazy as _

from planet.models import Post
from planet.settings import PLANET_CONFIG
from planet.utils import fetch_post_content

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Fetch and archive original content for posts where it is missing")

    def add_arguments(self, parser):
        parser.add_argument("--feed", type=int, help=_("Only process posts from this feed ID"))
        parser.add_argument("--limit", type=int, help=_("Maximum number of posts to process"))

    def handle(self, *args, **options):
        qs = Post.objects.filter(original_content__isnull=True)

        if options["feed"]:
            qs = qs.filter(feed_id=options["feed"])

        if options["limit"]:
            qs = qs[: options["limit"]]

        total = qs.count()
        logger.info("Fetching original content for %d posts.", total)

        delay = PLANET_CONFIG["FETCH_CONTENT_DELAY"]
        processed = 0

        for post in qs.iterator():
            logger.info("Fetching content for post %d: %s", post.id, post.url)
            post.original_content = fetch_post_content(post.url)
            post.save(update_fields=["original_content"])
            processed += 1
            if delay:
                time.sleep(delay)

        logger.info("Done: fetched content for %d/%d posts.", processed, total)
        self.stdout.write(
            _t("Done: fetched content for %(processed)d/%(total)d posts.") % {"processed": processed, "total": total}
        )
