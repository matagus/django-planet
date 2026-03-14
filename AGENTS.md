# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

django-planet is a **reusable Django app** for building RSS/Atom feed aggregator websites (planets). It is not a full Django project — it's installed as a dependency. An example project lives in `project/`.

## Common Commands

All commands use **Hatch** (install via `pipx install hatch`).

```bash
# Tests
hatch run test:test                    # run full test suite
hatch run test:cov                     # run with coverage report
hatch run test.py3.12-5.2:test         # specific Python/Django combo

# Direct test runner (useful for running a single test)
python -m django test tests.test_views.BlogViewsTest --settings tests.settings

# Example project
hatch run project:runserver            # runserver_plus
hatch run project:migrate
hatch run project:makemigrations
hatch run project:shell                # shell_plus

# Code quality
pre-commit run -a                      # ruff, black, codespell, pyupgrade
hatch run default:mypy planet project tests

# Docs
hatch run docs:serve
hatch run docs:build
```

## Architecture

### Repository Layout
- `planet/` — the reusable Django app (models, views, urls, admin, templatetags, management commands)
- `project/` — example Django project for local development
- `tests/` — test suite using Django's test runner + factory_boy (`tests/settings.py` for config)
- `docs/` — MkDocs documentation

### Models (`planet/models.py`)
Five models: **Blog** → **Feed** → **Post** ←M2M→ **Author** (via **PostAuthorData** junction table). Each model has a custom manager in `planet/managers.py` with chainable QuerySet methods (`for_blog()`, `for_feed()`, `for_author()`, `search()`).

### Views (`planet/views.py`)
Standard list/detail views for blogs, feeds, posts, and authors, plus a search dispatcher. All use `django-pagination-py3` for pagination.

### Feed Parsing (`planet/utils.py`)
`parse_feed()` uses feedparser to fetch and parse RSS/Atom feeds, with etag/last_modified support for efficient updates.

### Management Commands
- `planet_add_feed <url>` — adds a feed (auto-creates blog)
- `planet_update_all_feeds` — fetches new posts from all active feeds

## Testing

Tests use Django's test runner with factory_boy factories in `tests/factories.py`. Test settings use SQLite. The CI matrix covers Django 4.0–6.0 × Python 3.9–3.14 (see `pyproject.toml` for valid combinations).

## Code Style

- Line length: 120 (ruff and black)
- Pre-commit hooks enforce formatting — run `pre-commit install` on first setup
- When using Celery tasks triggered by model saves, always schedule via `transaction.on_commit()`
