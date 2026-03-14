import logging

from planet.models import Author, PostAuthorData

logger = logging.getLogger(__name__)


def create_authors_for_post(post, authors_data):
    for author_dict in authors_data:
        try:
            name = author_dict["name"].strip()
        except KeyError:
            logger.debug("Author entry missing 'name' key, skipping: %s", author_dict)
            continue

        if name:
            author, _ = Author.objects.get_or_create(name=name)
            PostAuthorData.objects.create(post=post, author=author)
