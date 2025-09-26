import hashlib

from time import mktime

from django.utils import timezone

import feedparser

from planet.settings import PLANET_CONFIG


def parse_feed(url, etag=None, modified=None):
    kwargs = dict(agent=PLANET_CONFIG["USER_AGENT"])

    if etag is None:
        if modified is None:
            pass
        else:
            kwargs["modified"] = modified
    else:
        kwargs["etag"] = etag

    return feedparser.parse(url, **kwargs)


def to_datetime(time_struct):
    try:
        # Create a timezone-aware datetime from the timestamp
        timestamp = mktime(time_struct)
        return timezone.datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
    except TypeError:
        return None


def md5_hash(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def normalize_language(value):
    if value is None:
        return

    return value.split("-")[0]
