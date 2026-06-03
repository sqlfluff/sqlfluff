#!/usr/bin/env python3
"""Assemble the published docs site tree for deployment."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vitepress-dist",
        type=Path,
        required=True,
        help="Path to the built VitePress dist directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Path where the assembled site tree should be written.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Top-level language segment to publish under.",
    )
    parser.add_argument(
        "--channel",
        default="latest",
        help="Version or channel name for the published VitePress build.",
    )
    parser.add_argument(
        "--title",
        help="Display title for this manifest entry.",
    )
    parser.add_argument(
        "--kind",
        choices=("channel", "release"),
        default="channel",
        help="Manifest entry kind for the published build.",
    )
    parser.add_argument(
        "--prerelease",
        action="store_true",
        help="Mark the manifest entry as a prerelease.",
    )
    parser.add_argument(
        "--published-at",
        help="Published date for release manifest entries.",
    )
    parser.add_argument(
        "--stable-release",
        help="Release version that the stable channel should point to.",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text content with a trailing newline."""
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def default_manifest() -> dict[str, Any]:
    """Build the default versions manifest for the beta site."""
    return {
        "default": "latest",
        "latest": "latest",
        "versions": [],
    }


def load_manifest(path: Path) -> dict[str, Any]:
    """Load the existing manifest if present, otherwise return defaults."""
    if not path.exists():
        return default_manifest()

    return json.loads(path.read_text(encoding="utf-8"))


def version_sort_key(entry: dict[str, Any]) -> tuple[int, tuple[int, ...] | str]:
    """Sort channels first, then releases in descending semantic version order."""
    key = str(entry["key"])

    if key == "latest":
        return (0, "latest")

    if key == "stable":
        return (1, "stable")

    try:
        parts = tuple(int(part) for part in key.split("."))
    except ValueError:
        return (3, key)

    return (2, tuple(-part for part in parts))


def upsert_manifest_entry(
    manifest: dict[str, Any],
    *,
    language: str,
    channel: str,
    title: str,
    kind: str,
    prerelease: bool,
    published_at: str | None,
    stable_release: str | None,
) -> dict[str, Any]:
    """Insert or update a manifest entry for the published channel."""
    entry: dict[str, Any] = {
        "key": channel,
        "label": channel,
        "title": title,
        "path": f"/{language}/{channel}/",
        "kind": kind,
        "builder": "vitepress",
        "prerelease": prerelease,
    }

    if published_at and kind == "release":
        entry["published_at"] = published_at

    versions = [
        existing
        for existing in manifest.get("versions", [])
        if existing.get("key") != channel
    ]
    versions.append(entry)
    versions.sort(key=version_sort_key)
    manifest["versions"] = versions

    if channel == "latest":
        manifest["latest"] = channel
        manifest.setdefault("default", channel)

    if stable_release:
        manifest["stable"] = stable_release

    return manifest


def build_redirects(language: str, manifest: dict[str, Any]) -> str:
    """Build the Netlify redirects file from the assembled manifest."""
    default_channel = str(manifest.get("default") or manifest.get("latest") or "latest")
    target = f"/{language}/{default_channel}/"
    return dedent(
        f"""
        / {target} 302
        /{language} {target} 302
        /{language}/ {target} 302
        """
    )


def build_global_headers(language: str) -> str:
    """Build generic cache-control headers for mutable channels and version assets."""
    return dedent(
        f"""
        /{language}/latest/
            Cache-Control: public, max-age=0, must-revalidate

        /{language}/latest/*
            Cache-Control: public, max-age=0, must-revalidate

        /{language}/stable/
            Cache-Control: public, max-age=0, must-revalidate

        /{language}/stable/*
            Cache-Control: public, max-age=0, must-revalidate

        /{language}/*/assets/*
            Cache-Control: public, max-age=31536000, immutable

        /{language}/*/vp-icons.css
            Cache-Control: public, max-age=31536000, immutable

        /{language}/versions.json
            Cache-Control: public, max-age=0, must-revalidate
        """
    )


def assemble_site(
    vitepress_dist: Path,
    output_dir: Path,
    language: str,
    channel: str,
    title: str,
    kind: str,
    prerelease: bool,
    published_at: str | None,
    stable_release: str | None,
) -> None:
    """Merge one built docs channel into the assembled site tree."""
    if not vitepress_dist.is_dir():
        raise FileNotFoundError(f"VitePress dist directory not found: {vitepress_dist}")

    target_dir = output_dir / language / channel
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        shutil.rmtree(target_dir)

    shutil.copytree(vitepress_dist, target_dir)

    manifest_path = output_dir / language / "versions.json"
    manifest = load_manifest(manifest_path)
    manifest = upsert_manifest_entry(
        manifest,
        language=language,
        channel=channel,
        title=title,
        kind=kind,
        prerelease=prerelease,
        published_at=published_at,
        stable_release=stable_release,
    )
    write_text(manifest_path, json.dumps(manifest, indent=2))
    write_text(output_dir / "_redirects", build_redirects(language, manifest))
    write_text(output_dir / "_headers", build_global_headers(language))


def main() -> int:
    """Main entry point."""
    args = parse_args()
    assemble_site(
        vitepress_dist=args.vitepress_dist,
        output_dir=args.output_dir,
        language=args.language.strip("/"),
        channel=args.channel.strip("/"),
        title=args.title
        or ("Development" if args.channel == "latest" else args.channel),
        kind=args.kind,
        prerelease=args.prerelease,
        published_at=args.published_at,
        stable_release=args.stable_release,
    )
    print(f"Assembled site written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
