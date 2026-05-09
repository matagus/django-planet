from unittest.mock import MagicMock


def _make_feed_data(
    href="https://example.com/feed.xml",
    title="",
    link="",
    feed_id="feed-id",
    subtitle="",
):
    """Create a mock feedparser feed_data object."""
    feed_data = MagicMock()
    feed_data.href = href
    feed_data.status = 200
    feed_data.bozo = False
    feed_data.entries = []
    feed_data.feed = {
        "title": title,
        "link": link,
        "subtitle": subtitle,
        "id": feed_id,
        "language": "en",
    }
    feed_data.get = lambda key, default=None: {
        "etag": None,
        "updated_parsed": None,
    }.get(key, default)
    return feed_data


def _make_entry_data(link="", title="", authors=None, author=""):
    """Create a mock feedparser entry_data object."""
    if authors is None:
        authors = []

    class MockEntryData(dict):
        def get(self, key, default=""):
            data = {
                "link": link,
                "title": title,
                "authors": authors,
                "author": author,
            }
            return data.get(key, default)

        @property
        def published_parsed(self):
            raise AttributeError("published_parsed")

        @property
        def summary_detail(self):
            raise AttributeError("summary_detail")

        @property
        def summary(self):
            return "Test summary"

    return MockEntryData()
