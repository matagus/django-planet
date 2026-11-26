# Models & Managers

## Model Relationships

django-planet uses five models with the following relationships:

```
Blog → Feed → Post ←M2M→ Author
                ↕
          PostAuthorData (junction table)
```

- A **Blog** has one or more **Feeds**
- A **Feed** belongs to one Blog and contains many **Posts**
- A **Post** belongs to one Feed and has many **Authors** (via PostAuthorData)
- An **Author** can have posts across multiple feeds and blogs

## Models

### Blog

Represents a blog or website whose feeds are aggregated.

Key fields: `title`, `url` (unique), `date_created`

### Feed

Stores detailed info about a parsed Atom or RSS feed.

Key fields: `blog` (FK), `url` (unique), `title`, `subtitle`, `language`, `guid` (unique, MD5 hash), `etag`, `last_modified`, `last_checked`, `is_active`

### Post

A single entry from a feed.

Key fields: `feed` (FK), `title`, `url`, `guid` (unique, MD5 hash), `content`, `original_content` (nullable — populated when [content archiving](usage.md#original-content-archiving) is enabled), `language`, `date_published`, `date_modified`, `date_created`

### Author

An author or contributor of posts.

Key fields: `name`, `email`, `profile_url`

### PostAuthorData

Junction table linking posts to authors, with an `is_contributor` flag to distinguish original authors from contributors.

## Custom Managers

Each model installs its manager with [`QuerySet.as_manager()`](https://docs.djangoproject.com/en/stable/topics/db/managers/#custom-managers-from-querysets),
so every method below lives on the QuerySet in `planet/managers.py` and is
available both on `Model.objects` and when chaining.

### BlogQuerySet

- `published()` — Blogs that have at least one checked feed
- `for_author(author)` — Blogs with posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)
- `get_or_create_stub(url)` — Get or create a blog using the URL host as its title
- `get_or_create_from_feed(feed_data)` — Get or create the blog a parsed feed belongs to

### FeedQuerySet

- `active()` — Feeds where `is_active=True`
- `published()` — Feeds that have been checked at least once
- `for_author(author)` — Feeds with posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)
- `get_by_url(url)` — Look a feed up by the hash of its URL
- `create_stub(url, blog)` — Create a placeholder feed before it is parsed
- `create_from(feed_data, blog)` — Create a feed from parsed feed data

### PostQuerySet

- `for_blog(blog)` — Posts from any feed belonging to the given blog
- `for_feed(feed)` — Posts from the given feed
- `for_author(author)` — Posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)
- `with_relations()` — Select/prefetch related Feed, Blog, and Authors
- `get_by_url(url)` — Look a post up by the hash of its URL
- `create_from(entry_data, feed)` — Create a post from a parsed entry, skipping duplicate URLs
- `create_authors_for_post(post, authors_data)` — Link an author set to a post, creating missing authors
- `create_with_authors(entry_data, feed)` — Create a post and its authors in one transaction

### AuthorQuerySet

- `for_blog(blog)` — Authors who have posts in feeds belonging to the given blog
- `search(query)` — Filter by name (case-insensitive contains)

All methods are chainable:

```python
Post.objects.for_blog(blog).search("django").with_relations()
```

Creation helpers live on the same QuerySets, so they work through `Model.objects`
and mid-chain alike:

```python
feed = Feed.objects.create_from(feed_data, blog)
post = Post.objects.create_with_authors(entry, feed)
```

For full field definitions and implementation details, see the [source code](https://github.com/matagus/django-planet/blob/main/planet/models.py).
