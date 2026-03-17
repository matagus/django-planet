# Admin Interface

Django-planet registers all models in the Django admin with search, filtering, and cross-linking between related objects.

## "Add Feed by URL" Workflow

The Feed admin has a special workflow for adding new feeds. When you click "Add Feed", you only need to provide the feed URL:

1. Enter the feed URL and click Save
2. django-planet automatically creates a **Blog** entry (using the feed's domain as a placeholder title) if one doesn't already exist
3. A **Feed** stub is created, ready to be populated on the next `planet_update_all_feeds` run

This is the same operation as `python manage.py planet_add_feed <url>`, but accessible from the admin.

!!! note

    The feed's title and metadata will be populated automatically the next time feeds are updated.

## BlogAdmin

- **List display:** title, URL, date created
- **Search:** by title, URL
- **Inline feeds:** Read-only tabular inline showing all feeds for the blog, with links to each feed's admin page

## FeedAdmin

- **List display:** title, URL, blog, language, etag, last modified, last checked, active status
- **List filter:** by language
- **Search:** by title, URL, blog title
- **Fieldsets:**
    - *General:* title, URL, blog, language
    - *Feed Status:* etag, last modified, last checked, is_active
    - *Authors:* read-only list of all authors who have posts in this feed, with links to each author's admin page

## PostAdmin

- **List display:** title, feed, guid, date published, date created
- **List filter:** by feed title, language
- **Search:** by title, blog title
- **Optimized queries:** uses `select_related` for feed and blog to minimize database queries

## AuthorAdmin

- **List display:** name, email
- **Search:** by name
- **Fieldsets:**
    - *General:* name, email, profile URL
    - *Feeds:* read-only list of all feeds this author has contributed to, with links to each feed's admin page

## PostAuthorDataAdmin

- **List display:** author name, is_contributor flag, post
- **List filter:** by is_contributor, author
