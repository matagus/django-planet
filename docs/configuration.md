# Configuration Reference

All django-planet settings are defined in a single `PLANET` dictionary in your Django settings module. Any key you don't specify falls back to its default.

## PLANET_CONFIG

```python
PLANET = {
    "USER_AGENT": "MyPlanet/1.0",
    "RECENT_POSTS_LIMIT": 10,
    "RECENT_BLOGS_LIMIT": 10,
    "POST_FILTER_BACKEND": "planet.backends.accept_all.AcceptAllBackend",
    "TOPIC_KEYWORDS": [],
    "FETCH_ORIGINAL_CONTENT": False,
    "FETCH_CONTENT_DELAY": 0,
}
```

### Settings Reference

`USER_AGENT`
:   **Type:** `str`
    **Default:** `"Django Planet/<version>"`

    The User-Agent header sent when fetching feeds and post content.

`RECENT_POSTS_LIMIT`
:   **Type:** `int`
    **Default:** `10`

    Number of posts shown by the `{% recent_posts %}` template tag.

`RECENT_BLOGS_LIMIT`
:   **Type:** `int`
    **Default:** `10`

    Number of blogs shown by the `{% recent_blogs %}` template tag.

`POST_FILTER_BACKEND`
:   **Type:** `str` (dotted Python path)
    **Default:** `"planet.backends.accept_all.AcceptAllBackend"`

    The backend class used to filter incoming feed entries before they are saved. See [Post Filter Backends](#post-filter-backends) below.

`TOPIC_KEYWORDS`
:   **Type:** `list[str]`
    **Default:** `[]`

    Keywords used by `KeywordFilterBackend` to filter posts. Only entries whose title or summary contains at least one keyword (case-insensitive) are accepted.

`FETCH_ORIGINAL_CONTENT`
:   **Type:** `bool`
    **Default:** `False`

    When `True`, django-planet fetches the full HTML of each post's original URL using `readability-lxml` and stores it in `Post.original_content`. See [Usage > Content Archiving](usage.md#original-content-archiving).

`FETCH_CONTENT_DELAY`
:   **Type:** `int | float`
    **Default:** `0`

    Seconds to wait between content fetches. Set this to a positive value (e.g., `1`) to be polite to origin servers.

## Post Filter Backends

By default, all feed entries are saved. You can configure a post filter backend to accept only relevant posts before they are stored.

### AcceptAllBackend (default)

```python
PLANET = {
    "POST_FILTER_BACKEND": "planet.backends.accept_all.AcceptAllBackend",
}
```

Accepts every entry unchanged. No configuration required.

### KeywordFilterBackend

```python
PLANET = {
    "POST_FILTER_BACKEND": "planet.backends.keyword.KeywordFilterBackend",
    "TOPIC_KEYWORDS": ["python", "django", "open source"],
}
```

Accepts entries whose title or summary contains at least one of the configured keywords (case-insensitive). Rejected entries are logged at `INFO` level.

When `TOPIC_KEYWORDS` is empty, the backend accepts all entries (fail-open).

### Writing a Custom Backend

Subclass `BasePostFilterBackend` and implement `filter_entries`:

```python
from planet.backends.base import BasePostFilterBackend


class MyBackend(BasePostFilterBackend):
    def filter_entries(self, entries, feed):
        # entries: list of feedparser entry objects
        # feed: planet.models.Feed instance
        return [e for e in entries if passes_my_check(e)]
```

Then point to it in your settings:

```python
PLANET = {
    "POST_FILTER_BACKEND": "myapp.backends.MyBackend",
}
```

## Logging

django-planet uses Python's standard `logging` module. All loggers use names under the `planet.*` namespace (e.g., `planet.utils`, `planet.management.commands.planet_update_all_feeds`).

Following Python library best practices, **no handlers are attached by default** — the host project controls all logging output. Add a `LOGGING` configuration to see log output:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "planet": {
            "handlers": ["console"],
            "level": "INFO",  # Use "DEBUG" for more verbosity
        },
    },
}
```

At `INFO` level you'll see feed add/update summaries and 304 skips. At `DEBUG` level you'll also see individual fetch details, per-entry creation, and `to_datetime()` edge cases.
