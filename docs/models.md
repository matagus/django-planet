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

Each model has a custom manager with chainable QuerySet methods.

### BlogManager

- `published()` — Blogs that have at least one checked feed
- `for_author(author)` — Blogs with posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)

### FeedManager

- `active()` — Feeds where `is_active=True`
- `published()` — Feeds that have been checked at least once
- `for_author(author)` — Feeds with posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)

### PostManager

- `for_blog(blog)` — Posts from any feed belonging to the given blog
- `for_feed(feed)` — Posts from the given feed
- `for_author(author)` — Posts by the given author
- `search(query)` — Filter by title (case-insensitive contains)
- `with_relations()` — Select/prefetch related Feed, Blog, and Authors

### AuthorManager

- `for_blog(blog)` — Authors who have posts in feeds belonging to the given blog
- `search(query)` — Filter by name (case-insensitive contains)

All QuerySet methods are chainable:

```python
Post.objects.for_blog(blog).search("django").with_relations()
```

For full field definitions and implementation details, see the [source code](https://github.com/matagus/django-planet/blob/main/planet/models.py).
