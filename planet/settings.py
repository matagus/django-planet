# -*- coding: utf-8 -*-
from django.conf import settings

try:
    PROJECT_PLANET = settings.PLANET
except AttributeError:
    PROJECT_PLANET = {}

PLANET_CONFIG = {
    "TAG_CLOUD_MIN_COUNT": 5,
    "BLOG_TAG_CLOUD_MIN_COUNT": 3,
    "FEED_TAG_CLOUD_MIN_COUNT": 3,
    "AUTHOR_TAG_CLOUD_MIN_COUNT": 3,
    "RELATED_TAGS_MIN_COUNT": 2,
}

PLANET_CONFIG.update(PROJECT_PLANET)
