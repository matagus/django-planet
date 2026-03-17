from django.conf import settings

from planet.__about__ import version

try:
    PROJECT_PLANET = settings.PLANET
except AttributeError:
    PROJECT_PLANET = {}


# These are the defaults
PLANET_CONFIG = {
    "USER_AGENT": f"Django Planet/{version}",
    "RECENT_POSTS_LIMIT": 10,
    "RECENT_BLOGS_LIMIT": 10,
    "POST_FILTER_BACKEND": "planet.backends.accept_all.AcceptAllBackend",
    "TOPIC_KEYWORDS": [],
    "FETCH_ORIGINAL_CONTENT": False,
    "FETCH_CONTENT_DELAY": 0,
}

PLANET_CONFIG.update(PROJECT_PLANET)
