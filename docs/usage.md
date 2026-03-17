# Usage

## Adding Feeds

Add a feed using the management command:

```bash
python manage.py planet_add_feed https://example.com/feed.xml
```

This will:

- Parse the feed and create a **Blog** entry if one doesn't already exist
- Create the **Feed** entry
- Import all posts from the feed
- Create **Author** entries and link them to posts

You can also add feeds through the Django admin interface — see [Admin Interface](admin.md) for details on the "Add Feed by URL" workflow.

## Updating Feeds

Fetch new posts from all active feeds:

```bash
python manage.py planet_update_all_feeds
```

This command:

- Iterates through all active feeds
- Uses **etag** and **last_modified** headers for efficient conditional requests (304 Not Modified)
- Creates new Post and Author entries as needed
- Updates feed metadata (last_checked, etag)

### Periodic Updates

For production, schedule `planet_update_all_feeds` to run periodically:

=== "Cron"

    ```bash
    # Run every hour
    0 * * * * /path/to/venv/bin/python /path/to/project/manage.py planet_update_all_feeds
    ```

=== "Celery"

    ```python
    # celery.py or tasks.py
    from celery import shared_task
    from django.core.management import call_command

    @shared_task
    def update_feeds():
        call_command("planet_update_all_feeds")

    # In your Celery beat schedule:
    CELERY_BEAT_SCHEDULE = {
        "update-feeds": {
            "task": "yourapp.tasks.update_feeds",
            "schedule": 3600,  # every hour
        },
    }
    ```

=== "systemd timer"

    Create `/etc/systemd/system/planet-update.service`:

    ```ini
    [Unit]
    Description=Update django-planet feeds

    [Service]
    Type=oneshot
    ExecStart=/path/to/venv/bin/python /path/to/project/manage.py planet_update_all_feeds
    User=www-data
    ```

    Create `/etc/systemd/system/planet-update.timer`:

    ```ini
    [Unit]
    Description=Run planet feed updates hourly

    [Timer]
    OnCalendar=hourly
    Persistent=true

    [Install]
    WantedBy=timers.target
    ```

    ```bash
    sudo systemctl enable --now planet-update.timer
    ```

## Original Content Archiving

By default, django-planet stores only the feed summary for each post. You can optionally fetch and archive the full original content from each post's URL.

### Enable Archiving

```python
PLANET = {
    "FETCH_ORIGINAL_CONTENT": True,
    "FETCH_CONTENT_DELAY": 1,  # seconds between fetches (be polite to servers)
}
```

When enabled, new posts will have their full content fetched automatically using `readability-lxml` to extract the article body. The result is stored in `Post.original_content` and displayed on the post detail page instead of the feed summary.

If fetching fails for a post, a WARNING is logged and `original_content` remains `None` — the feed summary is shown as fallback.

### Backfill Existing Posts

Use the `planet_fetch_post_content` command to backfill posts that were imported before archiving was enabled:

```bash
# Backfill all posts missing original_content
python manage.py planet_fetch_post_content

# Limit to a specific feed
python manage.py planet_fetch_post_content --feed 42

# Cap the number of posts processed
python manage.py planet_fetch_post_content --limit 100
```

## Management Commands Reference

### planet_add_feed

```
python manage.py planet_add_feed <feed_url>
```

Adds a new feed to the database. Creates the Blog (if it doesn't exist), Feed, Posts, and Authors.

### planet_update_all_feeds

```
python manage.py planet_update_all_feeds
```

Updates all active feeds. Fetches new posts, updates feed metadata (etag, last_checked), and creates new Post and Author entries as needed.

### planet_fetch_post_content

```
python manage.py planet_fetch_post_content [--feed <id>] [--limit <n>]
```

Backfills `original_content` for posts where it is missing.

| Argument | Description |
|----------|-------------|
| `--feed <id>` | Limit to posts from a specific feed (by feed ID) |
| `--limit <n>` | Cap the number of posts processed |

Respects `PLANET["FETCH_CONTENT_DELAY"]` between requests.

## Built-in Views

Django-planet provides a complete set of views with SEO-friendly URLs. If a request is missing the slug portion, it redirects permanently (301) to the canonical URL.

| URL Pattern | View Name | Template | Description |
|-------------|-----------|----------|-------------|
| `/` | `planet:index` | `planet/posts/list.html` | Post list (index page) |
| `/posts/` | `planet:post-list` | `planet/posts/list.html` | All posts |
| `/posts/<id>/<slug>/` | `planet:post-detail` | `planet/posts/detail.html` | Post detail |
| `/blogs/` | `planet:blog-list` | `planet/blogs/list.html` | All blogs |
| `/blogs/<id>/<slug>/` | `planet:blog-detail` | `planet/blogs/detail.html` | Blog detail (all posts from that blog) |
| `/feeds/` | `planet:feed-list` | `planet/feeds/list.html` | All feeds |
| `/feeds/<id>/<slug>/` | `planet:feed-detail` | `planet/feeds/detail.html` | Feed detail (all posts from that feed) |
| `/authors/` | `planet:author-list` | `planet/authors/list.html` | All authors |
| `/authors/<id>/<slug>/` | `planet:author-detail` | `planet/authors/detail.html` | Author detail (all posts by that author) |
| `/search/` | `planet:search` | *(dispatches to list views)* | Search endpoint |

## Search

The search endpoint (`/search/`) accepts GET parameters and dispatches to the appropriate list view:

| Parameter | Description |
|-----------|-------------|
| `q` | The search query string |
| `w` | What to search: `posts`, `blogs`, `feeds`, or `authors` |

Example: `/search/?q=python&w=posts` searches posts for "python".

The `SearchForm` is automatically available in all templates via the [context processor](installation.md#3-add-context-processor) as `search_form`.
