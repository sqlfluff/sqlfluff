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
    """Assert a published URL path maps to an existing file or directory."""
    relative_path = url_path.strip("/")
    path = site_dir / relative_path

    if path.is_dir():
        path = path / "index.html"

    if not path.is_file():
        raise FileNotFoundError(f"Missing {description}: {path}")


def smoke_check(site_dir: Path, language: str) -> None:
    """Validate the important assembled docs outputs."""
    manifest = load_manifest(site_dir, language)

    for entry in manifest["versions"]:
        key = entry.get("key")
        path = entry.get("path")

        if not key or not path:
            raise ValueError(f"Version entry must include key and path: {entry!r}")

        assert_path_exists(site_dir, str(path), f"index page for {key}")

    redirects_path = site_dir / "_redirects"

    if not redirects_path.is_file():
        raise FileNotFoundError(f"Missing Netlify redirects file: {redirects_path}")

    redirects = redirects_path.read_text(encoding="utf-8")
    default = str(manifest.get("default") or manifest.get("latest") or "latest")
    default_path = f"/{language}/{default}/"

    if not re.search(rf"^/ {re.escape(default_path)} 302$", redirects, re.MULTILINE):
        raise ValueError(f"Missing root redirect to {default_path}")

    assert_path_exists(site_dir, default_path, "default redirect target")

    headers_path = site_dir / "_headers"

    if not headers_path.is_file():
        raise FileNotFoundError(f"Missing Netlify headers file: {headers_path}")


def main() -> int:
    """Main entry point."""
    args = parse_args()
    smoke_check(args.site_dir, args.language.strip("/"))
    print(f"Smoke check passed for {args.site_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
