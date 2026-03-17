# django-planet

**A reusable Django app for building RSS/Atom feed aggregator websites (aka "Planet" sites).**

![Python Compatibility](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)
![Django Compatibility](https://img.shields.io/badge/django-4.0%20%7C%204.2%20%7C%205.0%20%7C%205.1%20%7C%205.2%20%7C%206.0-092E20.svg)
[![PyPi Version](https://img.shields.io/pypi/v/django-planet.svg)](https://pypi.python.org/pypi/django-planet)
![CI badge](https://github.com/matagus/django-planet/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/matagus/django-planet/graph/badge.svg?token=r3MXJJNLfo)](https://codecov.io/gh/matagus/django-planet)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Django-planet makes it easy to create a planet-style feed aggregator. Collect posts from multiple blogs and websites, store them in your database, and display them with built-in views and templates — or build your own custom front-end.

![Post List](img/post-list.png)

## Features

- **RSS and Atom feed parsing** — Supports both RSS and Atom feed formats via feedparser
- **Automatic feed updates** — Management commands to add feeds and update all feeds
- **Blog, Feed, Post, and Author models** — Complete data model with relationships
- **Built-in views and templates** — Ready-to-use views for blogs, feeds, posts, and authors
- **Django admin integration** — Manage all content through Django's admin interface, including an "Add Feed by URL" workflow
- **Search functionality** — Built-in search across posts, blogs, feeds, and authors
- **SEO-friendly URLs** — Slugified URLs with automatic redirects
- **Custom managers** — Chainable QuerySet methods for filtering by blog, feed, author
- **Template tags** — Custom template tags and filters for common operations
- **Pagination support** — Uses django-pagination-py3 for easy pagination
- **Post filtering** — Configurable filter backends to accept only relevant posts
- **Content archiving** — Optionally fetch and store the full original content of posts

## Quick Install

```bash
pip install django-planet
```

```python
INSTALLED_APPS = [
    # ...
    "planet",
    "pagination",
]

MIDDLEWARE = [
    # ...
    "pagination.middleware.PaginationMiddleware",
]
```

```bash
python manage.py migrate
```

See the [Installation](installation.md) guide for full setup instructions.

## Next Steps

- [Installation & Configuration](installation.md) — Full setup guide
- [Usage](usage.md) — Adding feeds, updating, views, and search
- [Configuration Reference](configuration.md) — All settings, filter backends, and logging
- [Demo & Screenshots](demo.md) — Live demo and example project
