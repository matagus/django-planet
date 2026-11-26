# Installation & Configuration

## Prerequisites

- Python 3.11–3.15
- Django 4.2–6.1

Supported combinations follow Django's own Python support policy:

| Django | Python |
| ------ | ------ |
| 4.2    | 3.11, 3.12 |
| 5.0    | 3.11, 3.12 |
| 5.1    | 3.11, 3.12 |
| 5.2    | 3.11, 3.12 |
| 6.0    | 3.12, 3.13, 3.14 |
| 6.1    | 3.12, 3.13, 3.14, 3.15 |

!!! note "Python 3.15 requires Django 6.1"

    Django only supports Python 3.15 starting with **Django 6.1.3**. If you use
    Python 3.15, make sure you install `Django>=6.1.3`.

### Upgrading to Django 6.1

django-planet itself requires no changes for Django 6.1, but keep these
upstream changes in mind for your own project:

- **Database versions**: Django 6.1 drops support for PostgreSQL 14,
  MySQL < 8.4, and MariaDB < 10.11, and requires SQLite 3.37+.
- **Cache keys**: cache keys for pages or template fragments that vary on
  headers or arguments changed in Django 6.1. The first request after
  upgrading will be a cache miss; no action is needed.

See the [Django 6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/)
for the full list of backwards-incompatible changes.

## Install

=== "pip"

    ```bash
    pip install django-planet
    ```

=== "From source"

    ```bash
    git clone https://github.com/matagus/django-planet.git
    cd django-planet
    pip install -e .
    ```

## Configure Your Django Project

### 1. Add to INSTALLED_APPS

Add `planet` and `pagination` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party apps
    "planet",
    "pagination",  # Required dependency
]
```

!!! warning "django.contrib.sites required"

    django-planet uses Django's sites framework. Make sure `django.contrib.sites` is in your
    `INSTALLED_APPS` and that you have `SITE_ID = 1` (or the appropriate site ID) in your settings.

### 2. Add Pagination Middleware

```python
MIDDLEWARE = [
    # ... other middleware
    "pagination.middleware.PaginationMiddleware",
]
```

### 3. Add Context Processor

Add the planet context processor to make `site`, `SITE_NAME`, `search_form`, and `PLANET_CONFIG` available in all templates:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # ... default context processors
                "planet.context_processors.context",
            ],
        },
    },
]
```

### 4. Include URL Configuration

```python
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("planet.urls")),  # or path("planet/", include("planet.urls"))
]
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Optional Settings

You can customize django-planet's behavior via the `PLANET` dict in your settings:

```python
PLANET = {
    "USER_AGENT": "MyPlanet/1.0",
    "RECENT_POSTS_LIMIT": 10,
    "RECENT_BLOGS_LIMIT": 10,
}
```

See the [Configuration Reference](configuration.md) for all available settings, including post filter backends and content archiving.
