#!/usr/bin/env python3
"""Assemble the published docs site tree for deployment."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from textwrap import dedent


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
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text content with a trailing newline."""
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_manifest(language: str, channel: str) -> dict[str, object]:
    """Build the initial versions manifest for the beta site."""
    return {
        "default": channel,
        "latest": channel,
        "versions": [
            {
                "key": channel,
                "label": channel,
                "title": "Development",
                "path": f"/{language}/{channel}/",
                "kind": "channel",
                "builder": "vitepress",
                "prerelease": False,
            }
        ],
    }


def build_redirects(language: str, channel: str) -> str:
    """Build the initial Netlify redirects file."""
    target = f"/{language}/{channel}/"
    return dedent(
        f"""
        / {target} 302
        /{language} {target} 302
        /{language}/ {target} 302
        """
    )


def build_headers(language: str, channel: str) -> str:
    """Build cache-control headers for the assembled site."""
    channel_root = f"/{language}/{channel}"
    return dedent(
        f"""
        {channel_root}/
          Cache-Control: public, max-age=0, must-revalidate

        {channel_root}/*
          Cache-Control: public, max-age=0, must-revalidate

        {channel_root}/assets/*
          Cache-Control: public, max-age=31536000, immutable

        {channel_root}/vp-icons.css
          Cache-Control: public, max-age=31536000, immutable

        /{language}/versions.json
          Cache-Control: public, max-age=0, must-revalidate
        """
    )


def assemble_site(vitepress_dist: Path, output_dir: Path, language: str, channel: str) -> None:
    """Create the assembled site tree for the latest docs channel."""
    if not vitepress_dist.is_dir():
        raise FileNotFoundError(f"VitePress dist directory not found: {vitepress_dist}")

    if output_dir.exists():
        shutil.rmtree(output_dir)

    target_dir = output_dir / language / channel
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(vitepress_dist, target_dir)

    manifest_path = output_dir / language / "versions.json"
    write_text(manifest_path, json.dumps(build_manifest(language, channel), indent=2))
    write_text(output_dir / "_redirects", build_redirects(language, channel))
    write_text(output_dir / "_headers", build_headers(language, channel))


def main() -> int:
    """Main entry point."""
    args = parse_args()
    assemble_site(
        vitepress_dist=args.vitepress_dist,
        output_dir=args.output_dir,
        language=args.language.strip("/"),
        channel=args.channel.strip("/"),
    )
    print(f"Assembled site written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())