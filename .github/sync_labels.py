#!/usr/bin/env python3
"""Synchronise GitHub issue labels with ``.github/labels.toml``.

The TOML file is the single source of truth: labels missing on the remote are
created, labels whose colour or description drifted are updated, and remote
labels that are not declared in the config are deleted (see ``--no-delete``).

Why this script exists
----------------------
The workflow used to run the ``labels`` CLI from PyPI (hackebrot/labels). That
project has had no release since 2020 and it deserialises API responses into a
strict ``attrs`` class, so it died the moment GitHub added the ``archived_at``
field to label objects (label archiving went GA on 2026-08-27)::

    TypeError: Label.__init__() got an unexpected keyword argument 'archived_at'

This replacement only uses the Python standard library and reads exactly the
fields it needs, so additional fields in API responses can never break it
again. TOML parsing uses the standard library :mod:`tomllib`, available on
Python 3.11 and newer.

Requires Python 3.11+.

Usage
-----
In CI (owner/repo/token come from the environment)::

    python .github/sync_labels.py

Locally::

    export GITHUB_TOKEN=ghp_xxx
    python .github/sync_labels.py --dry-run

Exit codes: ``0`` success, ``1`` an API call failed, ``2`` bad usage/config.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tomllib
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "2022-11-28"
USER_AGENT = "django-planet-label-sync"
PER_PAGE = 100
DESCRIPTION_MAX_LENGTH = 100

# Fields this script manages. Anything else GitHub returns (id, node_id, url,
# default, archived_at, ...) is deliberately ignored.
_NEXT_LINK = re.compile(r'<([^>]+)>;\s*rel="next"')


class SyncError(Exception):
    """Raised when the local config is invalid."""


def _normalise_color(color: str, *, label_name: str) -> str:
    """Return a colour as GitHub stores it: 6 lowercase hex digits, no ``#``."""
    value = color.strip().lstrip("#").lower()
    if not re.fullmatch(r"[0-9a-f]{6}", value):
        raise SyncError(f"label '{label_name}': invalid color {color!r} (expected RRGGBB)")
    return value


def read_config(path: Path) -> dict[str, dict[str, str]]:
    """Parse the labels TOML file into ``{name: {color, description}}``."""
    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except FileNotFoundError:
        raise SyncError(f"config file not found: {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"invalid TOML in {path}: {exc}") from None

    labels: dict[str, dict[str, str]] = {}
    for section, table in raw.items():
        if not isinstance(table, dict):
            raise SyncError(f"label '{section}': expected a TOML table")

        name = str(table.get("name", section)).strip()
        if name != section:
            raise SyncError(f"label '{section}': section name must equal the 'name' field " f"(got {name!r})")
        if not name:
            raise SyncError(f"label '{section}': name must not be empty")

        color = table.get("color")
        if not isinstance(color, str):
            raise SyncError(f"label '{name}': 'color' is required and must be a string")

        description = table.get("description", "") or ""
        if not isinstance(description, str):
            raise SyncError(f"label '{name}': 'description' must be a string")
        if len(description) > DESCRIPTION_MAX_LENGTH:
            raise SyncError(
                f"label '{name}': description is {len(description)} chars, "
                f"GitHub allows at most {DESCRIPTION_MAX_LENGTH}"
            )

        labels[name] = {
            "color": _normalise_color(color, label_name=name),
            "description": description.strip(),
        }
    return labels


def _request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, str], Any]:
    """Perform an API request, returning ``(status, headers, parsed_body)``."""
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", API_VERSION)
    request.add_header("User-Agent", USER_AGENT)
    if data is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            status = response.status
            headers = {k.lower(): v for k, v in response.headers.items()}
            body = response.read().decode()
    except urllib.error.HTTPError as exc:
        status = exc.code
        headers = {k.lower(): v for k, v in exc.headers.items()}
        body = exc.read().decode()
    except urllib.error.URLError as exc:
        raise SyncError(f"{method} {url} failed: {exc.reason}") from None

    parsed: Any = None
    if body.strip():
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = body.strip()
    return status, headers, parsed


def _error_detail(status: int, parsed: Any) -> str:
    """Build a readable error message from an API response."""
    if isinstance(parsed, dict):
        message = parsed.get("message") or parsed.get("error") or str(parsed)
        errors = parsed.get("errors")
        if errors:
            message = f"{message} ({errors})"
        return f"HTTP {status}: {message}"
    return f"HTTP {status}: {parsed}"


def list_labels(api_url: str, repo: str, token: str) -> list[dict[str, Any]]:
    """Return every label of ``repo``, following pagination."""
    labels: list[dict[str, Any]] = []
    url: str | None = f"{api_url}/repos/{repo}/labels?per_page={PER_PAGE}"
    while url:
        status, headers, parsed = _request("GET", url, token)
        if status != 200:
            raise SyncError(f"listing labels failed: {_error_detail(status, parsed)}")
        if not isinstance(parsed, list):
            raise SyncError(f"unexpected response listing labels: {parsed!r}")
        labels.extend(parsed)
        match = _NEXT_LINK.search(headers.get("link", ""))
        url = match.group(1) if match else None
    return labels


def _mutate(
    method: str,
    url: str,
    token: str,
    expected: int,
    action: str,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Run a create/update/delete call; report and swallow failures."""
    status, _, parsed = _request(method, url, token, payload)
    if status == expected:
        return True
    print(f"  !! {action} failed: {_error_detail(status, parsed)}", file=sys.stderr)
    return False


def compute_diff(
    local: dict[str, dict[str, str]],
    remote: list[dict[str, Any]],
    *,
    delete_extras: bool,
) -> dict[str, list[tuple[str, str | None, str | None]]]:
    """Group labels into create/update/delete/unchanged buckets.

    Each entry is ``(name, old_value, new_value)`` for the changed fields, so
    the report can show what actually differs.
    """
    remote_by_name: dict[str, dict[str, Any]] = {}
    for entry in remote:
        name = str(entry.get("name", ""))
        if name:
            remote_by_name[name] = entry

    buckets: dict[str, list[tuple[str, str | None, str | None]]] = {
        "create": [],
        "update": [],
        "delete": [],
        "unchanged": [],
    }

    for name, wanted in sorted(local.items()):
        current = remote_by_name.get(name)
        if current is None:
            buckets["create"].append((name, None, None))
            continue

        changes: list[tuple[str, str | None, str | None]] = []
        remote_color = str(current.get("color") or "").strip().lstrip("#").lower()
        if remote_color != wanted["color"]:
            changes.append(("color", remote_color, wanted["color"]))
        remote_description = (current.get("description") or "").strip()
        if remote_description != wanted["description"]:
            changes.append(("description", remote_description, wanted["description"]))

        if changes:
            for field, old, new in changes:
                buckets["update"].append((name, f"{field}: {old!r}", repr(new)))
        else:
            buckets["unchanged"].append((name, None, None))

    if delete_extras:
        for name in sorted(remote_by_name):
            if name not in local:
                buckets["delete"].append((name, None, None))

    return buckets


def _remote_meta(remote: list[dict[str, Any]], name: str) -> str:
    """Return a note about the remote label, e.g. its archived state."""
    for entry in remote:
        if str(entry.get("name", "")) == name and entry.get("archived_at"):
            return "  (archived remotely; archive state is left untouched)"
    return ""


def print_report(
    buckets: dict[str, list[tuple[str, str | None, str | None]]],
    remote: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> None:
    """Print what will happen (dry run) or what happened."""
    prefix = "Would " if dry_run else ""
    if buckets["create"]:
        print(f"{prefix}create {len(buckets['create'])} label(s):")
        for name, _, _ in buckets["create"]:
            print(f"  + {name}")
    if buckets["update"]:
        # Updates are recorded per changed field; report unique label names.
        names = sorted({name for name, _, _ in buckets["update"]})
        print(f"{prefix}update {len(names)} label(s):")
        for name in names:
            changes = [f"{old} -> {new}" for label_name, old, new in buckets["update"] if label_name == name]
            print(f"  ~ {name}: {', '.join(changes)}{_remote_meta(remote, name)}")
    if buckets["delete"]:
        print(f"{prefix}delete {len(buckets['delete'])} label(s):")
        for name, _, _ in buckets["delete"]:
            print(f"  - {name}")
    if not (buckets["create"] or buckets["update"] or buckets["delete"]):
        print("Nothing to do: remote labels already match the config.")
    else:
        print(f"Unchanged: {len({n for n, _, _ in buckets['unchanged']})} label(s)")


def apply_changes(
    buckets: dict[str, list[tuple[str, str | None, str | None]]],
    local: dict[str, dict[str, str]],
    *,
    api_url: str,
    repo: str,
    token: str,
) -> bool:
    """Apply create/update/delete calls. Returns False if any call failed."""
    base = f"{api_url}/repos/{repo}/labels"
    ok = True

    # Delete first so a rename in the config cannot collide with an existing
    # label (GitHub rejects duplicate names on create).
    for name, _, _ in buckets["delete"]:
        url = f"{base}/{urllib.parse.quote(name, safe='')}"
        print(f"Deleting '{name}' ...")
        ok &= _mutate("DELETE", url, token, 204, f"deleting '{name}'")

    for name in sorted({n for n, _, _ in buckets["update"]}):
        wanted = local[name]
        url = f"{base}/{urllib.parse.quote(name, safe='')}"
        print(f"Updating '{name}' ...")
        ok &= _mutate(
            "PATCH",
            url,
            token,
            200,
            f"updating '{name}'",
            {
                "new_name": name,
                "color": wanted["color"],
                "description": wanted["description"],
            },
        )

    for name, _, _ in buckets["create"]:
        wanted = local[name]
        print(f"Creating '{name}' ...")
        ok &= _mutate(
            "POST",
            base,
            token,
            201,
            f"creating '{name}'",
            {
                "name": name,
                "color": wanted["color"],
                "description": wanted["description"],
            },
        )
    return ok


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    default_owner, _, default_repo = repository.partition("/")

    parser = argparse.ArgumentParser(
        description="Sync GitHub issue labels from a TOML config.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path(".github/labels.toml"),
        help="path to the labels TOML file (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--owner",
        default=default_owner or None,
        help="repository owner (default: from $GITHUB_REPOSITORY)",
    )
    parser.add_argument(
        "-r",
        "--repo",
        default=default_repo or None,
        help="repository name (default: from $GITHUB_REPOSITORY)",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
        help="GitHub token (default: $GITHUB_TOKEN or $GH_TOKEN)",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        help="GitHub API root (default: $GITHUB_API_URL or https://api.github.com)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="report what would change without touching the remote",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="keep remote labels that are missing from the config",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    missing = [
        f"--{name}" for name, value in (("owner", args.owner), ("repo", args.repo), ("token", args.token)) if not value
    ]
    if missing:
        print(
            f"error: missing required value(s): {', '.join(missing)} "
            "(set GITHUB_REPOSITORY / GITHUB_TOKEN or pass them explicitly)",
            file=sys.stderr,
        )
        return 2

    repo = f"{args.owner}/{args.repo}"
    try:
        local = read_config(args.config)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Repository: {repo}")
    print(f"Config:     {args.config} ({len(local)} label(s))")

    try:
        remote = list_labels(args.api_url, repo, args.token)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Remote:     {len(remote)} label(s)")
    print()

    buckets = compute_diff(local, remote, delete_extras=not args.no_delete)
    print_report(buckets, remote, dry_run=args.dry_run)

    if args.dry_run:
        return 0
    if not (buckets["create"] or buckets["update"] or buckets["delete"]):
        return 0

    print()
    try:
        ok = apply_changes(
            buckets,
            local,
            api_url=args.api_url,
            repo=repo,
            token=args.token,
        )
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
