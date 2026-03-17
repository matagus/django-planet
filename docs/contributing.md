# Contributing

Contributions are welcome!

## Development Setup

1. Fork and clone the repository:

    ```bash
    git clone https://github.com/YOUR_USERNAME/django-planet.git
    cd django-planet
    ```

2. Install development dependencies:

    ```bash
    pip install -e .
    pip install pre-commit
    ```

3. Set up pre-commit hooks:

    ```bash
    pre-commit install
    ```

4. Verify everything works:

    ```bash
    pre-commit run --all-files
    hatch run test:test
    ```

## Repository Layout

```
planet/          # The reusable Django app (models, views, urls, admin, templatetags, management commands)
project/         # Example Django project for local development
tests/           # Test suite using Django's test runner + factory_boy
docs/            # MkDocs documentation (this site)
```

## Architecture Overview

### Models

Five models: **Blog** -> **Feed** -> **Post** <-M2M-> **Author** (via **PostAuthorData** junction table). Each model has a custom manager in `planet/managers.py` with chainable QuerySet methods. See [Models & Managers](models.md) for details.

### Views

Standard list/detail views for blogs, feeds, posts, and authors, plus a search dispatcher. All use `django-pagination-py3` for pagination. See [Usage > Built-in Views](usage.md#built-in-views).

### Feed Parsing

`parse_feed()` in `planet/utils.py` uses feedparser to fetch and parse RSS/Atom feeds, with etag/last_modified support for efficient conditional requests.

### Management Commands

- `planet_add_feed <url>` — adds a feed (auto-creates blog)
- `planet_update_all_feeds` — fetches new posts from all active feeds
- `planet_fetch_post_content` — backfills original post content

## Running Tests

### With Hatch (recommended)

```bash
# Run full test suite across all Python/Django combinations
hatch run test:test

# Run with coverage report
hatch run test:cov

# Run for a specific Python/Django combination
hatch run test.py3.12-5.2:test

# View all available test environments
hatch env show test
```

### Without Hatch

```bash
# Install test dependencies
pip install coverage factory_boy

# Run tests
python -m django test --settings tests.settings

# Run a specific test
python -m django test tests.test_views.BlogViewsTest --settings tests.settings

# Run with coverage
coverage run -m django test --settings tests.settings
coverage report
```

## Code Style

- **Line length:** 120 characters
- **Formatting:** ruff + black (enforced by pre-commit hooks)
- **Linting:** ruff, codespell, pyupgrade
- **Type checking:** `hatch run default:mypy planet project tests`

## After Any Change

After making any change to the codebase, always do these three things in order:

1. **Run pre-commit hooks** (formatting, linting):

    ```bash
    pre-commit run -a
    ```

2. **Run the full test suite:**

    ```bash
    hatch run test:test
    ```

3. **Regenerate translation files:**

    ```bash
    cd planet/ && hatch run django-admin makemessages -l es --settings=tests.settings
    ```

## Translation Workflow

django-planet supports internationalization. To update or generate translation files, you must run `makemessages` from inside the `planet/` directory:

```bash
cd planet/
hatch run django-admin makemessages -l es --settings=tests.settings
```

## Pull Request Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Follow the [After Any Change](#after-any-change) checklist
4. Commit your changes: `git commit -m "Add my feature"`
5. Push to your fork: `git push origin feature/my-feature`
6. Open a Pull Request against `main`
