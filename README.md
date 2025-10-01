# django-planet

![Python Compatibility](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)
![Django Compatibility](https://img.shields.io/badge/django-4.0%20%7C%204.2%20%7C%205.0%20%7C%205.1%20%7C%205.2-092E20.svg)
[![PyPi Version](https://img.shields.io/pypi/v/django-planet.svg)](https://pypi.python.org/pypi/django-planet)
![CI badge](https://github.com/matagus/django-planet/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/matagus/django-planet/graph/badge.svg?token=r3MXJJNLfo)](https://codecov.io/gh/matagus/django-planet)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

**A reusable Django app for building RSS/Atom feed aggregator websites (aka "Planet" sites).**

Django-planet makes it easy to create a planet-style feed aggregator. Collect posts from multiple blogs and websites, store them in your database, and display them with built-in views and templates—or build your own custom front-end.

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

## 📦 Installation & Configuration

### Via pip

```bash
pip install django-planet
```

### From source

```bash
git clone https://github.com/matagus/django-planet.git
cd django-planet
pip install -e .
```

### Configure your Django project

1. Add `planet` and `pagination` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "planet",
    "pagination",  # Required dependency
]
```

2. Add pagination middleware to `MIDDLEWARE` in `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware
    "pagination.middleware.PaginationMiddleware",
]
```

3. (Optional) Configure planet settings in `settings.py`:

```python
PLANET = {
    "USER_AGENT": "MyPlanet/1.0",  # Customize the User-Agent for feed requests
    "RECENT_POSTS_LIMIT": 10,  # Number of recent posts to show
    "RECENT_BLOGS_LIMIT": 10,  # Number of recent blogs to show
}
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Include planet URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("planet.urls")),  # or path("planet/", include("planet.urls"))
]
```

## 📖 Usage

### Adding Feeds

You can add feeds using the management command:

```bash
python manage.py planet_add_feed https://example.com/feed.xml
```

This will:
- Parse the feed and create a Blog entry if it doesn't exist
- Create the Feed entry
- Import all posts from the feed
- Create Author entries and link them to posts

### Updating Feeds

Update all active feeds to fetch new posts:

```bash
python manage.py planet_update_all_feeds
```

This command:
- Iterates through all feeds
- Fetches new entries
- Creates new Post and Author entries as needed
- Updates feed metadata (last_checked, etag)

**Set up periodic updates:**

For production, schedule this command to run periodically:

**Using cron:**
```bash
# Run every hour
0 * * * * /path/to/venv/bin/python /path/to/project/manage.py planet_update_all_feeds
```

### Built-in Views

Django-planet provides these URL patterns:

- `/` - Post list (index)
- `/posts/` - All posts
- `/posts/<id>/<slug>/` - Post detail
- `/blogs/` - All blogs
- `/blogs/<id>/<slug>/` - Blog detail (shows all posts from that blog)
- `/feeds/` - All feeds
- `/feeds/<id>/<slug>/` - Feed detail (shows all posts from that feed)
- `/authors/` - All authors
- `/authors/<id>/<slug>/` - Author detail (shows all posts by that author)
- `/search/` - Search form endpoint

### Templates

Planet includes a complete set of templates:

```
planet/templates/planet/
├── base.html                    # Base template
├── posts/
│   ├── list.html               # Post list view
│   ├── detail.html             # Post detail view
│   └── blocks/
│       └── list.html           # Reusable post list block
├── blogs/
│   ├── list.html               # Blog list view
│   ├── detail.html             # Blog detail view
│   └── blocks/
│       └── list.html           # Reusable blog list block
├── feeds/
│   ├── list.html               # Feed list view
│   ├── detail.html             # Feed detail view
│   └── blocks/
│       └── list_for_author.html
└── authors/
    ├── list.html               # Author list view
    ├── detail.html             # Author detail view
    └── blocks/
        ├── list.html           # Reusable author list block
        └── list_for_feed.html
```

### Using Template Tags

Django-planet includes custom template tags for common operations. Load them in your templates:

```django
{% load planet_tags %}
```

#### Available Template Tags

##### Filters

**`clean_html`** - Cleans HTML content by removing inline styles, style tags, and script tags

```django
{{ post.content|clean_html }}
```

This filter:
- Removes inline `style` attributes
- Removes `<style>` and `<script>` tags
- Replaces multiple consecutive `<br/>` tags (3+) with just two
- Returns safe HTML that won't be escaped

##### Simple Tags

**`get_first_paragraph`** - Extracts the first paragraph or sentence from post content

```django
{% get_first_paragraph post.content as excerpt %}
{{ excerpt }}
```

This tag:
- Strips all HTML tags
- Normalizes whitespace
- Returns the first sentence longer than 80 characters
- Falls back to the first 80 characters if no long sentence is found
- Useful for creating post excerpts or previews

**`get_authors_for_blog`** - Returns all authors who have written posts for a specific blog

```django
{% get_authors_for_blog blog as authors %}
{% for author in authors %}
  <a href="{{ author.get_absolute_url }}">{{ author.name }}</a>
{% endfor %}
```

**`blogs_for_author`** - Returns all blogs that an author has contributed to

```django
{% blogs_for_author author as blogs %}
{% for blog in blogs %}
  <a href="{{ blog.get_absolute_url }}">{{ blog.title }}</a>
{% endfor %}
```

##### Inclusion Tags

Inclusion tags render complete HTML blocks with their own templates.

**`authors_for_feed`** - Renders a list of all authors who have posts in a feed

```django
{% authors_for_feed feed %}
```

Uses template: `planet/authors/blocks/list_for_feed.html`

**`feeds_for_author`** - Renders a list of all feeds an author has contributed to

```django
{% feeds_for_author author %}
```

Uses template: `planet/feeds/blocks/list_for_author.html`

**`recent_posts`** - Renders a list of the most recent posts across all blogs

```django
{% recent_posts %}
```

Uses template: `planet/posts/blocks/list.html`
Limit controlled by `PLANET["RECENT_POSTS_LIMIT"]` setting (default: 10)

**`recent_blogs`** - Renders a list of the most recently added blogs

```django
{% recent_blogs %}
```

Uses template: `planet/blogs/blocks/list.html`
Limit controlled by `PLANET["RECENT_BLOGS_LIMIT"]` setting (default: 10)

### Admin Interface

All models are registered in Django admin with sensible defaults:

- **BlogAdmin**
- **FeedAdmin**
- **PostAdmin**
- **AuthorAdmin**

All admin interfaces include search and filtering capabilities.

### Management Commands

**`planet_add_feed <feed_url>`**
- Adds a new feed to the database
- Creates Blog if it doesn't exist
- Imports all existing posts from the feed
- Creates Author entries for post authors

**`planet_update_all_feeds`**
- Updates all active feeds
- Fetches new posts from each feed
- Updates feed metadata (etag, last_checked)
- Creates new Post and Author entries as needed

## 📸 Screenshots

### Post List
![Post List](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/post-list.png)

### Blog View
![Blog View](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/blog.png)

### Full Post View
![Full Post View](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/full-post.png)

### Live Demo

Check out the live demo: [django-planet.matagus.dev](https://django-planet.matagus.dev/)

Demo source code is available in the `project/` directory.

## 🧪 Testing

You can run tests either with Hatch (recommended for testing multiple Python/Django versions) or directly.

### With Hatch (recommended)

Django-planet uses [Hatch](https://hatch.pypa.io/) for testing across multiple Python and Django versions.

#### Run all tests

Test across all Python/Django version combinations:

```bash
hatch run test:test
```

#### Run tests for specific versions

```bash
# Python 3.12 + Django 5.0
hatch run test.py3.12-5.0:test

# Python 3.11 + Django 5.1
hatch run test.py3.11-5.1:test
```

#### Run with coverage

```bash
hatch run test:cov
```

This will:
1. Run tests with coverage tracking
2. Generate a coverage report
3. Output results to the terminal

#### View test matrix

See all available Python/Django test combinations:

```bash
hatch env show test
```


### Without Hatch

If you prefer to run tests directly without Hatch:

1. Install test dependencies:
   ```bash
   pip install coverage factory_boy
   ```

2. Run tests using Django's test runner:
   ```bash
   python -m django test --settings tests.settings
   ```

3. Run tests with coverage:
   ```bash
   coverage run -m django test --settings tests.settings
   coverage report
   ```

4. Generate coverage JSON:
   ```bash
   coverage json
   ```

## 🤝 Contributing

Contributions are welcome! ❤️

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-planet.git
   cd django-planet
   ```

3. Install development dependencies:
   ```bash
   pip install -e .
   pip install pre-commit
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

   This will automatically run code quality checks (ruff, black, codespell, etc.) before each commit.

5. (Optional) Run pre-commit on all files manually:
   ```bash
   pre-commit run --all-files
   ```

### Quick Contribution Guide

1. Create a feature branch (`git checkout -b feature/new-feature`)
2. Make your changes
3. Run tests (see above)
4. Pre-commit hooks will run automatically when you commit
5. Commit your changes (`git commit -m 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Open a Pull Request

## 📄 License

`django-planet` is released under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for more information.

## 🙏 Acknowledgements

Developed and built using:

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Inspired by:
- [Feedjack](http://www.feedjack.org/) - Original Django feed aggregator
- [Mark Pilgrim's Feedparser](https://feedparser.readthedocs.io/) - Universal feed parser library

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/matagus/django-planet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matagus/django-planet/discussions)
- **PyPI**: [pypi.org/project/django-planet](https://pypi.org/project/django-planet)
