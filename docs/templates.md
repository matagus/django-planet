# Templates & Tags

## Template Directory

Django-planet includes a complete set of templates:

```
planet/templates/planet/
├── base.html
├── posts/
│   ├── list.html
│   ├── detail.html
│   └── blocks/
│       └── list.html
├── blogs/
│   ├── list.html
│   ├── detail.html
│   └── blocks/
│       └── list.html
├── feeds/
│   ├── list.html
│   ├── detail.html
│   └── blocks/
│       └── list_for_author.html
└── authors/
    ├── list.html
    ├── detail.html
    └── blocks/
        ├── list.html
        └── list_for_feed.html
```

## Overriding Templates

Django-planet templates can be overridden using Django's standard template loading mechanism. Place your custom templates in your project's template directory, matching the same path structure:

```
your_project/
└── templates/
    └── planet/
        └── posts/
            └── list.html    # Overrides planet's default post list
```

Make sure your project's template directory is listed before `APP_DIRS` in your `TEMPLATES` setting, or use `DIRS` to specify it explicitly.

## Template Tags Reference

Load the template tags in any template:

```django
{% load planet_tags %}
```

### Filters

#### clean_html

Cleans HTML content by extracting the readable article body using `readability-lxml`. Removes clutter like navigation, ads, and extraneous markup, returning just the main content.

```django
{{ post.content|clean_html }}
```

Returns safe HTML (won't be escaped).

### Simple Tags

#### get_first_paragraph

Extracts the first paragraph or sentence from post content. Useful for creating excerpts.

```django
{% get_first_paragraph post.content as excerpt %}
<p>{{ excerpt }}</p>
```

How it works:

- Strips all HTML tags
- Normalizes whitespace
- Returns the first sentence longer than 80 characters
- Falls back to the first 80 characters if no long sentence is found

#### get_authors_for_blog

Returns all authors who have written posts for a specific blog.

```django
{% get_authors_for_blog blog as authors %}
{% for author in authors %}
    <a href="{{ author.get_absolute_url }}">{{ author.name }}</a>
{% endfor %}
```

#### blogs_for_author

Returns all blogs that an author has contributed to.

```django
{% blogs_for_author author as blogs %}
{% for blog in blogs %}
    <a href="{{ blog.get_absolute_url }}">{{ blog.title }}</a>
{% endfor %}
```

#### post_titles

Returns a comma-separated string of post titles from a queryset.

```django
{% post_titles posts limit=5 as titles %}
<p>{{ titles }}</p>
```

| Argument | Default | Description |
|----------|---------|-------------|
| `posts` | *(required)* | A Post queryset |
| `limit` | `5` | Maximum number of titles to include |

### Inclusion Tags

Inclusion tags render complete HTML blocks using their own templates.

#### authors_for_feed

Renders a list of all authors who have posts in a feed.

```django
{% authors_for_feed feed %}
```

**Template:** `planet/authors/blocks/list_for_feed.html`

#### feeds_for_author

Renders a list of all feeds an author has contributed to.

```django
{% feeds_for_author author %}
```

**Template:** `planet/feeds/blocks/list_for_author.html`

#### recent_posts

Renders a list of the most recent posts across all blogs.

```django
{% recent_posts %}
```

**Template:** `planet/posts/blocks/list.html`

Limit controlled by `PLANET["RECENT_POSTS_LIMIT"]` (default: 10).

#### recent_blogs

Renders a list of the most recently added blogs.

```django
{% recent_blogs %}
```

**Template:** `planet/blogs/blocks/list.html`

Limit controlled by `PLANET["RECENT_BLOGS_LIMIT"]` (default: 10).

## Context Processor

The `planet.context_processors.context` processor makes the following variables available in all templates:

| Variable | Description |
|----------|-------------|
| `site` | The current `Site` object (from `django.contrib.sites`) |
| `SITE_NAME` | The site's name (`site.name`) |
| `search_form` | A `SearchForm` instance (pre-filled if search params are in the GET request) |
| `PLANET_CONFIG` | The full planet configuration dictionary |

Add it to your template context processors — see [Installation](installation.md#3-add-context-processor).
