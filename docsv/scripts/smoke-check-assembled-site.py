#!/usr/bin/env python3
"""Smoke check the assembled versioned docs site."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-dir",
        type=Path,
        required=True,
        help="Path to the assembled site tree.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Top-level language segment to validate.",
    )
    return parser.parse_args()


def load_manifest(site_dir: Path, language: str) -> dict[str, Any]:
    """Load and minimally validate the versions manifest."""
    manifest_path = site_dir / language / "versions.json"

    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing versions manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    versions = manifest.get("versions")

    if not isinstance(versions, list) or not versions:
        raise ValueError("versions.json must include at least one version entry")

    return manifest


def assert_path_exists(site_dir: Path, url_path: str, description: str) -> None:
    """Assert a published URL path maps to a file inside the assembled tree.

    The path is confined to `site_dir` before it is used. A manifest entry is
    only as trustworthy as whatever produced it, and one containing `..` would
    otherwise let this check pass by finding a real file outside the tree — which
    would vouch for a version that was never published.
    """
    # Stripping the slashes makes a rooted URL path relative, so there is no
    # absolute case left to test for here; traversal is what remains.
    relative_path = url_path.strip("/")

    if not relative_path:
        raise ValueError(f"Empty path for {description}")

    if ".." in relative_path.split("/"):
        raise ValueError(f"Unsafe path for {description}: {url_path!r}")

    path = site_dir / relative_path

    # Resolve both sides so a symlink cannot point out of the tree either.
    if not path.resolve().is_relative_to(site_dir.resolve()):
        raise ValueError(
            f"Path escapes the site directory for {description}: {url_path!r}"
        )

    if path.is_dir():
        path = path / "index.html"

    # Netlify serves `foo.html` for `/foo`, and the permalink rules rely on it:
    # their destinations are suffix-less so one rule can serve versions whose
    # builds put the page in a different file. Resolving the same way here keeps
    # the check honest about what the deployed site will do.
    #
    # Containment is re-checked afterwards rather than only on the path above:
    # `resolve()` follows symlinks, so a link at the `.html` name could otherwise
    # satisfy this check with a file outside the tree — vouching for a page the
    # deployed site does not have.
    if not path.is_file() and not path.suffix:
        path = path.with_suffix(".html")

        if not path.resolve().is_relative_to(site_dir.resolve()):
            raise ValueError(
                f"Path escapes the site directory for {description}: {url_path!r}"
            )

    if not path.is_file():
        raise FileNotFoundError(f"Missing {description}: {path}")


# The picker loads these from the language root, so an archived version that was
# built once and frozen picks up later changes to them. A publish that dropped
# them would take the picker off every archived version at once.
SHARED_ASSETS = ("version-picker.js", "version-picker.css")


def smoke_check(site_dir: Path, language: str) -> None:
    """Validate the important assembled docs outputs."""
    manifest = load_manifest(site_dir, language)
    listed = 0

    for entry in manifest["versions"]:
        key = entry.get("key")
        path = entry.get("path")

        if not key or not path:
            raise ValueError(f"Version entry must include key and path: {entry!r}")

        assert_path_exists(site_dir, str(path), f"index page for {key}")

        # Absent means listed, so a manifest written before the flag existed
        # still counts.
        if entry.get("listed", True):
            listed += 1

    # An all-unlisted manifest is a site whose picker offers nothing, which
    # would look like the picker being broken rather than like a publishing
    # mistake.
    if not listed:
        raise ValueError("At least one version entry must be listed in the picker")

    # Where the versions the picker does not list stay discoverable. Without it
    # the picker's "All versions" entry is a link to a 404.
    assert_path_exists(site_dir, f"/{language}/versions.html", "archive index page")

    # Netlify only serves a 404 page from the publish root; it does not fall back
    # to the one inside a version. Without this file every miss on the site gets
    # Netlify's own generic page instead of ours.
    assert_path_exists(site_dir, "/404.html", "site 404 page")

    for asset in SHARED_ASSETS:
        assert_path_exists(
            site_dir, f"/{language}/shared/{asset}", f"shared asset {asset}"
        )

    redirects_path = site_dir / "_redirects"

    if not redirects_path.is_file():
        raise FileNotFoundError(f"Missing Netlify redirects file: {redirects_path}")

    redirects = redirects_path.read_text(encoding="utf-8")
    default = str(manifest.get("default") or manifest.get("latest") or "latest")
    default_path = f"/{language}/{default}/"

    if not re.search(rf"^/ {re.escape(default_path)} 302$", redirects, re.MULTILINE):
        raise ValueError(f"Missing root redirect to {default_path}")

    assert_path_exists(site_dir, default_path, "default redirect target")

    # Every SQLFluff release from 2.0.0 onward prints these URLs from the CLI,
    # and they are not files in any version — the rules are the only thing that
    # makes them resolve, on new and already-published versions alike.
    permalink_rules = [
        line.split()
        for line in redirects.splitlines()
        if line.startswith(f"/{language}/:version/")
    ]

    if not permalink_rules:
        raise ValueError(f"Missing permalink redirect rules for /{language}/:version/")

    # Spot-checked against the channel the site root serves, which is the one a
    # reader following a CLI link actually lands on.
    for source, destination, *_ in permalink_rules:
        assert_path_exists(
            site_dir,
            destination.replace(":version", default).split("#")[0],
            f"permalink target for {source}",
        )

    headers_path = site_dir / "_headers"

    if not headers_path.is_file():
        raise FileNotFoundError(f"Missing Netlify headers file: {headers_path}")

    headers = headers_path.read_text(encoding="utf-8")

    # The shared assets have fixed filenames rather than fingerprints, so an
    # immutable or missing rule here is what would keep a picker fix from
    # reaching frozen versions.
    if f"/{language}/shared/*" not in headers:
        raise ValueError(f"Missing cache-control rule for /{language}/shared/*")


def main() -> int:
    """Main entry point."""
    args = parse_args()
    smoke_check(args.site_dir, args.language.strip("/"))
    print(f"Smoke check passed for {args.site_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
