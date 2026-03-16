import logging

from planet.backends.base import BasePostFilterBackend
from planet.settings import PLANET_CONFIG

logger = logging.getLogger(__name__)


class KeywordFilterBackend(BasePostFilterBackend):
    def __init__(self):
        self.keywords = [kw.lower() for kw in PLANET_CONFIG.get("TOPIC_KEYWORDS", [])]

    def filter_entries(self, entries, feed):
        if not self.keywords:
            return list(entries)

        accepted = []
        for entry in entries:
            text = (getattr(entry, "title", "") + " " + getattr(entry, "summary", "")).lower()
            if any(kw in text for kw in self.keywords):
                accepted.append(entry)
            else:
                logger.info("Rejected entry '%s' from feed '%s': no keyword match", getattr(entry, "title", ""), feed)
        return accepted
