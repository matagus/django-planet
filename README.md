# django-planet

![Python Compatibility](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)
![Django Compatibility](https://img.shields.io/badge/django-4.0%20%7C%204.2%20%7C%205.0%20%7C%205.1%20%7C%205.2%20%7C%206.0-092E20.svg)
[![PyPi Version](https://img.shields.io/pypi/v/django-planet.svg)](https://pypi.python.org/pypi/django-planet)
![CI badge](https://github.com/matagus/django-planet/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/matagus/django-planet/graph/badge.svg?token=r3MXJJNLfo)](https://codecov.io/gh/matagus/django-planet)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Docs](https://img.shields.io/badge/docs-readthedocs-blue)](https://django-planet.readthedocs.io/)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://django-planet.matagus.dev/)

**A reusable Django app for building RSS/Atom feed aggregator websites (aka "Planet" sites).**

Django-planet makes it easy to create a planet-style feed aggregator. Collect posts from multiple blogs and websites, store them in your database, and display them with built-in views and templates—or build your own custom front-end.

**Live Demo**: [A planet for Django-related feeds](https://django-planet.matagus.dev/)

![Post List](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/post-list.png)

## ✨ Features

- **RSS and Atom feed parsing** - Supports both RSS and Atom feed formats via feedparser
- **Automatic feed updates** - Management commands to add feeds and update all feeds
- **Blog, Feed, Post, and Author models** - Complete data model with relationships
- **Built-in views and templates** - Ready-to-use views for blogs, feeds, posts, and authors
- **Django admin integration** - Manage all content through Django's admin interface
- **Search functionality** - Built-in search across posts, blogs, feeds, and authors
- **SEO-friendly URLs** - Slugified URLs with automatic redirects
- **Custom managers** - QuerySet methods for filtering by blog, feed, author
- **Template tags** - Custom template tags for common operations
- **Pagination support** - Uses django-pagination-py3 for easy pagination
- **Post filtering** - Configurable filter backends to accept only relevant posts
- **Content archiving** - Optionally fetch and store the full original content of posts

## 📦 Quick Start

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

Then include the URLs in your `urls.py`:

```python
path("", include("planet.urls")),
```

→ [Full installation & configuration guide](https://django-planet.readthedocs.io/en/latest/installation/)

## 📖 Documentation

- [Installation & Configuration](https://django-planet.readthedocs.io/en/latest/installation/) — Setup, settings reference, and URL configuration
- [Usage](https://django-planet.readthedocs.io/en/latest/usage/) — Adding feeds, updating feeds, built-in views, and search
- [Models](https://django-planet.readthedocs.io/en/latest/models/) — Data model and relationships
- [Templates & Template Tags](https://django-planet.readthedocs.io/en/latest/templates/) — Built-in templates and custom tags
- [Admin Interface](https://django-planet.readthedocs.io/en/latest/admin/) — Managing content via Django admin
- [Configuration Reference](https://django-planet.readthedocs.io/en/latest/configuration/) — All settings, post filtering backends, and logging
- [Contributing](https://django-planet.readthedocs.io/en/latest/contributing/) — Development setup and contribution guide
- [Demo & Screenshots](https://django-planet.readthedocs.io/en/latest/demo/) — Live demo and example project

## 🧪 Testing

```bash
hatch run test:test   # full suite
hatch run test:cov    # with coverage
```

See the [contributing guide](https://django-planet.readthedocs.io/en/latest/contributing/) for the full test matrix and setup instructions.

## 📄 License

`django-planet` is released under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for more information.

## 🙏 Acknowledgements

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Inspired by [Feedjack](http://www.feedjack.org/) and [Mark Pilgrim's Feedparser](https://feedparser.readthedocs.io/).

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/matagus/django-planet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matagus/django-planet/discussions)
- **PyPI**: [pypi.org/project/django-planet](https://pypi.org/project/django-planet)
