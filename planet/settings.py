# -*- coding: utf-8 -*-
from django.conf import settings

try:
    PROJECT_PLANET = settings.PLANET
except AttributeError:
    PROJECT_PLANET = {}


version = "1.0.0"

# These are the defaults
PLANET_CONFIG = {
    'USER_AGENT': f"Django Planet/{version}",
    'RECENT_POSTS_LIMIT': 10,
    'RECENT_BLOGS_LIMIT': 10,
}

PLANET_CONFIG.update(PROJECT_PLANET)
