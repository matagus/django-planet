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
│       ├── list.html
│       └── post_list.html
├── blogs/
│   ├── list.html
│   └── detail.html
├── feeds/
│   ├── list.html
│   └── detail.html
├── authors/
│   ├── list.html
│   └── detail.html
└── blocks/
    ├── nav_list.html
    └── breadcrumb_blog.html
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

#### attr

Resolves an attribute by name; missing attributes yield an empty string.
Methods are called if they take no arguments. Output is auto-escaped.

```django
{% attr obj "title" as label %}
{{ label }}
```

### Inclusion Tags

All four sidebar tags below render the same template,
`planet/blocks/nav_list.html`: a heading plus one link per item. Each tag picks
the attribute used as link text (`Author.name`, `Feed.title`, `Post.title`,
`Blog.title`). To change the markup or labels, override that template in your
project.

#### authors_for_feed

Renders a list of all authors who have posts in a feed.

```django
{% authors_for_feed feed %}
```

**Template:** `planet/blocks/nav_list.html`

#### feeds_for_author

Renders a list of all feeds an author has contributed to.

```django
{% feeds_for_author author %}
```

**Template:** `planet/blocks/nav_list.html`

#### recent_posts

Renders a list of the most recent posts across all blogs.

```django
{% recent_posts %}
```

**Template:** `planet/blocks/nav_list.html`

Limit controlled by `PLANET["RECENT_POSTS_LIMIT"]` (default: 10).

#### recent_blogs

Renders a list of the most recently added blogs.

```django
{% recent_blogs %}
```

**Template:** `planet/blocks/nav_list.html`

Limit controlled by `PLANET["RECENT_BLOGS_LIMIT"]` (default: 10).

### Shared Partials

#### planet/posts/blocks/post_list.html

Paginated list of post summaries, included by the blog, feed and author detail
views and the post list view.

```django
{% include "planet/posts/blocks/post_list.html" %}
```

| Variable | Default | Description |
|----------|---------|-------------|
| `posts` | *(required)* | Post queryset, paginated 10 per page |
| `container_class` | `container px-0` | Classes for the wrapper element |
| `post_wrapper_class` | `post row` | Classes for each post element |

Pass overrides with the `with` keyword:

```django
{% include "planet/posts/blocks/post_list.html" with container_class="content" %}
```

Override this template in your project to change how every post list renders.

#### planet/blocks/breadcrumb_blog.html

Breadcrumb trail to a blog: *Blogs > blog title*. Included by the feed and post
detail views; requires `blog` in the context.

```django
{% include "planet/blocks/breadcrumb_blog.html" with blog=post.feed.blog %}
```

### Pagination

Planet ships a Bootstrap-styled `pagination/pagination.html` that overrides the
plain default from `django-pagination-py3`, so `{% paginate %}` renders styled
page links out of the box. This requires `planet` before `pagination` in
`INSTALLED_APPS` (see [Installation](installation.md#1-add-to-installed_apps)).
To customize it, place your own `pagination/pagination.html` in your project's
template directory (loaded before `APP_DIRS`).

## Context Processor

The `planet.context_processors.context` processor makes the following variables available in all templates:

| Variable | Description |
|----------|-------------|
| `site` | The current `Site` object (from `django.contrib.sites`) |
| `SITE_NAME` | The site's name (`site.name`) |
| `search_form` | A `SearchForm` instance (pre-filled if search params are in the GET request) |
| `PLANET_CONFIG` | The full planet configuration dictionary |

Add it to your template context processors — see [Installation](installation.md#3-add-context-processor).
