#!/usr/bin/env python3
"""Inject the shared version picker into a built Sphinx HTML tree.

Archived pre-cutover versions are Sphinx builds. They have no picker of their
own and are never rebuilt, so the picker has to be added after the fact and has
to come from a location above the version — `/en/shared/`, which every publish
refreshes. This adds the two tags that load it to every page's `<head>`.

It works on any Sphinx output, whether rebuilt from a tag or mirrored from Read
the Docs. That is what keeps mirroring available as a fallback for a version
which will no longer build: both routes converge here.

Stripping the Read the Docs addons injection is part of the same pass, because a
mirrored page would otherwise keep asking readthedocs.org for a flyout that
advertises the site being replaced.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# The whole of what Read the Docs adds to a served page: one script, plus the
# four `readthedocs-*` meta tags it reads its configuration from. Both were
# appended immediately before `</head>` on every version back to 0.9.0.
RTD_INJECTION = re.compile(
    r"<script[^>]*readthedocs-addons\.js[^>]*>\s*</script>"
    r'|<meta\s+name="readthedocs-[^"]*"[^>]*/?>',
    re.IGNORECASE,
)

HEAD_CLOSE = re.compile(r"</head>", re.IGNORECASE)

# Matching on the filename rather than on the full tag: it is what makes the
# pass idempotent, and it must keep matching if the tags below gain attributes.
INJECTION_MARKER = "version-picker.js"


def build_tags(shared_base: str) -> str:
    """Build the markup added to every page's head.

    `shared_base` is an absolute URL rather than a path relative to the page,
    which would vary with the page's depth. Sphinx output is otherwise
    base-agnostic — every internal link it emits is relative, which is why an
    archived build can be dropped at any path — but the picker reads the
    language root out of `location.pathname` and fetches the manifest from it, so
    it is already tied to the `/<language>/<version>/` layout. One absolute
    prefix does not give up anything the picker had.
    """
    return (
        f'<link rel="stylesheet" href="{shared_base}version-picker.css">'
        f'<script src="{shared_base}version-picker.js" defer></script>'
    )


def process(path: Path, tags: str, strip_rtd: bool) -> bool:
    """Rewrite one HTML file, returning whether it changed."""
    # `errors="replace"` rather than a failure: these are historical builds, and
    # one page with a decoding problem should not stop a version being archived.
    original = path.read_text(encoding="utf-8", errors="replace")
    updated = RTD_INJECTION.sub("", original) if strip_rtd else original

    if INJECTION_MARKER not in updated:
        # A page with no `</head>` is not an alabaster page. Leaving it exactly
        # as built is the right answer for a search index or a raw asset that
        # happens to carry an `.html` suffix.
        updated, count = HEAD_CLOSE.subn(tags + "</head>", updated, count=1)

        if not count:
            return False

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def inject(html_dir: Path, shared_base: str, strip_rtd: bool = True) -> int:
    """Inject the picker across a built tree, returning the pages changed."""
    if not html_dir.is_dir():
        raise FileNotFoundError(f"HTML directory not found: {html_dir}")

    tags = build_tags(shared_base)

    return sum(
        process(path, tags, strip_rtd) for path in sorted(html_dir.rglob("*.html"))
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_dir", type=Path, help="Built Sphinx HTML directory.")
    parser.add_argument(
        "--shared-base",
        default="/en/shared/",
        help="Absolute URL prefix the shared picker assets are published under.",
    )
    parser.add_argument(
        "--keep-rtd",
        action="store_true",
        help="Leave any Read the Docs addons injection in place.",
    )
    args = parser.parse_args()

    changed = inject(args.html_dir, args.shared_base, not args.keep_rtd)
    print(f"Injected shared picker into {changed} pages under {args.html_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
