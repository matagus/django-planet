# Installation & Configuration

## Prerequisites

- Python 3.9+
- Django 4.0+

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
