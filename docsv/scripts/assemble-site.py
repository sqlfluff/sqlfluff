#!/usr/bin/env python3
"""Assemble the published docs site tree for deployment."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path, PurePosixPath, PureWindowsPath
from textwrap import dedent
from typing import Any

SHARED_ASSETS = Path(__file__).resolve().parent.parent / "shared"
DEFAULT_REDIRECTS = (
    Path(__file__).resolve().parent.parent / ".vitepress" / "redirects.json"
)

# The placeholder Netlify substitutes into the destination. One rule per
# permalink then covers every published version, rather than one rule per
# permalink per version — which would be 204 rules a release and would pass
# Netlify's recommended ceiling within a handful of them.
VERSION_PLACEHOLDER = ":version"

# A redirect chain longer than this is a configuration mistake rather than
# something to follow patiently.
MAX_CHAIN = 8


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    # Named for what it holds rather than for what built it: archived Sphinx
    # versions are published through this same script.
    parser.add_argument(
        "--dist",
        type=Path,
        required=True,
        help="Path to the built docs directory to publish for this version.",
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
        help="Version or channel name for the published build.",
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
        "--builder",
        choices=("vitepress", "sphinx"),
        default="vitepress",
        help="Which toolchain produced this build.",
    )
    parser.add_argument(
        "--prerelease",
        action="store_true",
        help="Mark the manifest entry as a prerelease.",
    )
    parser.add_argument(
        "--unlisted",
        action="store_true",
        help=(
            "Keep this version out of the picker's list. It stays published, "
            "reachable by URL, and listed on the archive index page."
        ),
    )
    parser.add_argument(
        "--published-at",
        help="Published date for release manifest entries.",
    )
    parser.add_argument(
        "--stable-release",
        help="Release version that the stable channel should point to.",
    )
    parser.add_argument(
        "--shared-dir",
        type=Path,
        default=SHARED_ASSETS,
        help="Directory of shared runtime assets to publish at the language root.",
    )
    parser.add_argument(
        "--redirects",
        type=Path,
        default=DEFAULT_REDIRECTS,
        help="Permalink map to generate versioned redirect rules from.",
    )
    parser.add_argument(
        "--allow-missing-redirect-targets",
        action="store_true",
        help="Warn instead of failing when a permalink target has no built page.",
    )
    return parser.parse_args()


def assert_safe_segment(value: str, name: str) -> None:
    """Reject a path segment which would escape the tree it is joined into.

    `channel` and `language` become directory names under the output directory,
    and the channel is deleted and rewritten on every run. Since a manual publish
    takes the channel from an operator-supplied version, a value containing a
    separator or `..` would place that delete outside the assembled site.

    Both path flavours are checked rather than only the running one, so the answer
    does not depend on the platform. A drive-qualified value such as ``C:foo`` is
    neither absolute nor separated, and relocates a path only on Windows — but the
    Linux runner which publishes the site is exactly where we would want to find
    out, rather than on a maintainer's machine.
    """
    if not value or value != value.strip():
        raise ValueError(f"{name} must not be empty or padded: {value!r}")

    # Separators are rejected on the raw string, before any parsing. Parsing
    # normalises `.` away — `PurePath("foo/.").parts` is `("foo",)` — so a value
    # containing a separator can otherwise look like a single segment while
    # naming a directory the manifest does not record. Both separators are
    # listed regardless of platform, for the same reason the flavours below are.
    if set(value) & {"/", "\\"}:
        raise ValueError(f"{name} must be a single path segment: {value!r}")

    if value in {os.curdir, os.pardir}:
        raise ValueError(f"{name} must not be a relative reference: {value!r}")

    for flavour in (PurePosixPath, PureWindowsPath):
        candidate = flavour(value)

        # `root` as well as `drive` and `is_absolute`: on Windows a lone `\` is
        # rooted without being absolute, which would put the delete below at the
        # drive root.
        if candidate.drive or candidate.root or candidate.is_absolute():
            raise ValueError(f"{name} must be a relative path segment: {value!r}")

        # Parsing must round-trip to exactly the value as one component. This
        # catches `C:foo`, which Windows splits into a drive and a name.
        if candidate.parts != (value,):
            raise ValueError(f"{name} must be a single path segment: {value!r}")


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


# The release forms this project has actually tagged: a dotted release number,
# optionally a prerelease such as `4.0.0a1` or `0.7.0a8`, optionally a
# post-release such as `4.0.1.post1`. Separators are accepted loosely because
# PEP 440 permits several spellings of the same version and the tags predate any
# convention being enforced.
RELEASE_PATTERN = re.compile(
    r"""
    ^(?P<release>\d+(?:\.\d+)*)
    (?:[-_.]?(?P<stage>a|b|c|rc|alpha|beta|pre|preview)[-_.]?(?P<stage_num>\d*))?
    (?:[-_.]?post[-_.]?(?P<post>\d*))?$
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Enough components for `major.minor.patch.micro`; anything shorter is padded so
# `3.4` and `3.4.0` compare as the same release.
RELEASE_DEPTH = 4

# Prerelease stages in PEP 440 order, so `4.0.0a2` is older than `4.0.0b1` rather
# than being compared on its number alone. Only `aN` has ever been tagged here,
# which is why this went unnoticed; the ordering is cheap to get right and the
# manifest's ordering decides which release readers are warned about.
STAGE_ORDER = {
    "a": 0,
    "alpha": 0,
    "b": 1,
    "beta": 1,
    "c": 2,
    "rc": 2,
    "pre": 2,
    "preview": 2,
}

# One above every prerelease stage, so a final release outranks all of them.
FINAL_STAGE = max(STAGE_ORDER.values()) + 1


def version_sort_key(entry: dict[str, Any]) -> tuple[int, tuple[int, ...] | str]:
    """Sort channels first, then releases in descending version order.

    The manifest's *ordering* is load-bearing rather than cosmetic: the stale
    version notice treats any release which is not the first as superseded, so a
    version sorted into the wrong place is a version readers are wrongly warned
    about — or wrongly not warned about.

    Ordering within releases is descending, which is why every numeric component
    is negated. A version which does not parse keeps its own bucket after the
    releases rather than being forced into the numeric order, since guessing
    where it belongs would be worse than putting it somewhere predictable.
    """
    key = str(entry["key"])

    if key == "latest":
        return (0, "latest")

    if key == "stable":
        return (1, "stable")

    match = RELEASE_PATTERN.match(key)

    if not match:
        return (3, key)

    parts = [int(part) for part in match["release"].split(".")][:RELEASE_DEPTH]
    parts += [0] * (RELEASE_DEPTH - len(parts))

    # A prerelease precedes the release it leads up to, and a post-release
    # follows it: `4.0.0a1` < `4.0.0b1` < `4.0.0` < `4.0.1.post1`. Ranking the
    # stage above the prerelease number keeps `4.0.0` ahead of every `4.0.0aN`,
    # which a bare number could not express — there is no prerelease number that
    # means "not a prerelease".
    stage = (match["stage"] or "").lower()
    stage_rank = STAGE_ORDER.get(stage, FINAL_STAGE) if stage else FINAL_STAGE
    stage_num = int(match["stage_num"] or 0)
    post = int(match["post"] or 0)

    return (2, tuple(-part for part in (*parts, stage_rank, stage_num, post)))


def upsert_manifest_entry(
    manifest: dict[str, Any],
    *,
    language: str,
    channel: str,
    title: str,
    kind: str,
    builder: str,
    prerelease: bool,
    unlisted: bool,
    published_at: str | None,
    stable_release: str | None,
) -> dict[str, Any]:
    """Insert or update a manifest entry for the published channel."""
    previous = next(
        (
            existing
            for existing in manifest.get("versions", [])
            if existing.get("key") == channel
        ),
        None,
    )

    entry: dict[str, Any] = {
        "key": channel,
        "label": channel,
        "title": title,
        "path": f"/{language}/{channel}/",
        "kind": kind,
        "builder": builder,
        "prerelease": prerelease,
        # Unlisted versions stay published and reachable; they are simply not
        # offered in the picker, which no comparable project fills with patch
        # releases. The archive index page is where they are discoverable.
        "listed": not unlisted,
    }

    # The entry is rebuilt from scratch rather than merged, so anything not
    # passed in is dropped. That is fine for values this script is told on every
    # run, but a release's publication date is only known to the release event
    # which first published it. Rebuilding an existing release without repeating
    # `--published-at` would silently erase the date, which the version picker
    # displays. So an explicit value wins, and otherwise an existing one is
    # carried forward. A brand new release with no date simply has none.
    resolved_published_at = published_at or (
        previous.get("published_at") if previous else None
    )

    if resolved_published_at and kind == "release":
        entry["published_at"] = resolved_published_at

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


def load_redirect_map(path: Path) -> dict[str, str]:
    """Load the permalink map, dropping comment keys and rejecting bad entries.

    A malformed entry is rejected rather than skipped. Skipping would leave that
    URL a 404 while the publish reported success, which is the failure this whole
    mechanism exists to remove.
    """
    if not path.is_file():
        print(f"Warning: no permalink map at {path}; no redirect rules written")
        return {}

    entries = json.loads(path.read_text(encoding="utf-8"))
    # `_comment` is the convention these config files use for notes.
    permalinks = {
        key: value for key, value in entries.items() if not key.startswith("_")
    }

    # Whitespace is checked as well as emptiness because `_redirects` is a
    # space-delimited format: a target of `"   "` is not merely useless, it
    # produces `/en/:version/perma/x /en/:version/    301`, a rule that parses as
    # something nobody wrote. Non-strings are rejected here so the rule builder
    # can assume it has text to work with.
    invalid = sorted(
        key
        for key, value in permalinks.items()
        if not isinstance(value, str)
        or not value
        or any(character.isspace() for character in f"{key}{value}")
    )

    if invalid:
        raise ValueError(
            f"Permalinks with an empty or whitespace-bearing entry in {path}: "
            f"{', '.join(invalid)}"
        )

    return permalinks


def split_fragment(target: str) -> tuple[str, str]:
    """Split a redirect target into its path and its `#fragment`."""
    path, separator, fragment = target.partition("#")
    return path, separator + fragment


def follow_chain(redirects: dict[str, str], target: str) -> tuple[str, str]:
    """Resolve a permalink target which is itself a permalink.

    The map contains one of these — `internals` points at `perma/internals`,
    which points at the page. The client-side handler followed it by accident,
    because each hop 404s and re-runs the handler. A rule has to do it on
    purpose, and sending the reader through two redirects when one will do is a
    wasted round trip.
    """
    path, fragment = split_fragment(target)
    seen: list[str] = []

    while True:
        key = path.strip("/")

        if key not in redirects:
            return path, fragment

        if key in seen or len(seen) >= MAX_CHAIN:
            raise ValueError(
                f"Redirect chain does not terminate: {' -> '.join(seen + [key])}"
            )

        seen.append(key)
        path, next_fragment = split_fragment(redirects[key])
        # The final hop names the heading it wants; an earlier one is only kept
        # if nothing later replaces it.
        fragment = next_fragment or fragment


def resolve_redirect_targets(
    dist: Path,
    redirects: dict[str, str],
    allow_missing: bool = False,
) -> None:
    """Check every permalink still lands on a page in the build being published.

    Nothing downstream needs the answer — the rules are written with suffix-less
    destinations, which Netlify resolves itself. This exists because a permalink
    is a promise: every SQLFluff release from `2.0.0` onward prints these URLs
    from the CLI, so a target lost to a page rename should fail the publish that
    renamed it rather than redirect a reader from a 404 to a 404.

    Only meaningful against a VitePress build. An archived Sphinx version lays
    its pages out differently and carries its own `sphinx-reredirects` pages, so
    the caller skips this for those.
    """
    missing = []

    for key, target in sorted(redirects.items()):
        path, _ = follow_chain(redirects, target)
        relative = path.strip("/")

        if relative and not any(
            (dist / candidate).is_file()
            for candidate in (f"{relative}.html", f"{relative}/index.html")
        ):
            missing.append(f"{key} -> {target}")

    if not missing:
        return

    detail = "\n".join(f"  - {item}" for item in missing)
    message = f"{len(missing)} permalink target(s) have no built page:\n{detail}"

    if not allow_missing:
        raise FileNotFoundError(message)

    print(f"Warning: {message}")


def build_permalink_rules(language: str, redirects: dict[str, str]) -> list[str]:
    """Build one Netlify rule per permalink, covering every published version.

    `:version` is a placeholder, so these rules are written once and apply to
    every version under the language root — including versions published before
    this code existed, which is the only way those get fixed: the permalinks were
    never files, and re-running the publish workflow for an old tag rebuilds it
    from that tag's source, which does not know about them.

    Both suffix forms are emitted because both are in the wild: the CLI prints
    `perma/<name>.html`, and a reader who trims it gets the suffix-less form.
    Netlify ignores a trailing slash when matching, so that case needs no rule.

    Nothing is forced with `!`, so a version which already has a real file at one
    of these paths keeps serving it. That is what leaves the archived Sphinx
    versions alone: their `sphinx-reredirects` pages are correct for their own
    page layout, and these rules are not.
    """
    rules = []

    for key in sorted(redirects):
        source = f"/{language}/{VERSION_PLACEHOLDER}/{key.strip('/')}"
        path, fragment = follow_chain(redirects, redirects[key])
        destination = f"/{language}/{VERSION_PLACEHOLDER}/{path.strip('/')}{fragment}"

        # A suffix-less destination, which Netlify resolves to whichever of
        # `x.html` and `x/index.html` the target version built. Naming the file
        # would bake the current build's layout into rules that also serve older
        # versions.
        rules.append(f"{source} {destination} 301")
        rules.append(f"{source}.html {destination} 301")

    return rules


def default_channel(manifest: dict[str, Any]) -> str:
    """The channel the site root serves, and so the one the site speaks as.

    Shared by the root redirect and the site-wide 404 page, which must name the
    same channel: a 404 offering to send the reader somewhere other than where
    `/` goes would be its own small confusion.
    """
    versions = [
        str(version["key"])
        for version in manifest.get("versions", [])
        if version.get("key")
    ]
    channel = str(manifest.get("default") or manifest.get("latest") or "latest")

    if channel not in versions and versions:
        channel = "latest" if "latest" in versions else versions[0]

    return channel


def build_redirects(
    language: str,
    manifest: dict[str, Any],
    redirects: dict[str, str] | None = None,
) -> str:
    """Build the Netlify redirects file from the assembled manifest."""
    target = f"/{language}/{default_channel(manifest)}/"
    lines = [
        f"/ {target} 302",
        f"/{language} {target} 302",
        f"/{language}/ {target} 302",
    ]

    if redirects:
        lines.append("")
        lines.extend(build_permalink_rules(language, redirects))

    return "\n".join(lines) + "\n"


def build_global_headers(language: str) -> str:
    """Build generic cache-control headers for mutable channels and version assets.

    The shared assets get a short cache rather than an immutable one. They are
    published at fixed filenames — an archived Sphinx build injects
    `/en/shared/version-picker.js` into every page and is never rebuilt — so
    there is no fingerprint to change, and a long cache would mean a picker fix
    reaching frozen versions only once browsers expired it.
    """
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

        /{language}/versions.html
            Cache-Control: public, max-age=0, must-revalidate

        /{language}/shared/*
            Cache-Control: public, max-age=300, must-revalidate
        """
    )


VERSIONS_PAGE_STYLE = """
    :root { color-scheme: light dark; }
    body {
        max-width: 46rem;
        margin: 0 auto;
        padding: 3rem 1.25rem 5rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            "Helvetica Neue", Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #24292f;
        background: #ffffff;
    }
    h1 { margin: 0 0 0.5rem; font-size: 1.9rem; }
    h2 {
        margin: 2.5rem 0 0.75rem;
        padding-bottom: 0.35rem;
        font-size: 1.15rem;
        border-bottom: 1px solid #d8dee4;
    }
    p.lede { margin: 0 0 1rem; color: #57606a; }
    ul { margin: 0; padding: 0; list-style: none; }
    li {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        gap: 0.6rem;
        padding: 0.35rem 0;
        border-bottom: 1px solid #f0f2f4;
    }
    li a { font-weight: 600; text-decoration: none; color: #0969da; }
    li a:hover { text-decoration: underline; }
    .version { font-variant-numeric: tabular-nums; }
    .meta { color: #57606a; font-size: 0.85rem; }
    .tag {
        padding: 0 0.35rem;
        font-size: 0.75rem;
        color: #57606a;
        background: #eff1f3;
        border-radius: 3px;
    }
    footer { margin-top: 3rem; color: #57606a; font-size: 0.85rem; }
    footer a { color: #0969da; }
    @media (prefers-color-scheme: dark) {
        body { color: #e6edf3; background: #0d1117; }
        h2 { border-bottom-color: #30363d; }
        li { border-bottom-color: #21262d; }
        p.lede, .meta, footer { color: #9198a1; }
        li a, footer a { color: #4493f8; }
        .tag { color: #9198a1; background: #21262d; }
    }
"""


def entry_series(entry: dict[str, Any]) -> str:
    """The major series heading a release belongs under, such as `3.x`."""
    match = RELEASE_PATTERN.match(str(entry["key"]))
    return f"{match['release'].split('.')[0]}.x" if match else "Other"


def release_groups(manifest: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    """Group the released versions by major series, keeping manifest order."""
    groups: dict[str, list[dict[str, Any]]] = {}

    for entry in manifest.get("versions", []):
        if entry.get("kind") == "channel" or entry.get("key") in {"latest", "stable"}:
            continue

        groups.setdefault(entry_series(entry), []).append(entry)

    return list(groups.items())


def render_version_item(entry: dict[str, Any], stable_key: str | None) -> str:
    """Render one list item on the archive index page."""
    path = html.escape(str(entry.get("path") or ""), quote=True)
    label = html.escape(str(entry.get("title") or entry.get("label") or entry["key"]))

    tags = []

    if entry.get("key") == stable_key:
        tags.append("current release")
    if entry.get("prerelease"):
        tags.append("pre-release")
    if entry.get("builder") == "sphinx":
        tags.append("archived")

    parts = [f'<a class="version" href="{path}">{label}</a>']
    parts += [f'<span class="tag">{html.escape(tag)}</span>' for tag in tags]

    if entry.get("published_at"):
        published = html.escape(str(entry["published_at"]))
        parts.append(f'<span class="meta">{published}</span>')

    return "<li>" + "".join(parts) + "</li>"


def build_versions_page(language: str, manifest: dict[str, Any]) -> str:
    """Render the archive index listing every published version.

    The picker deliberately lists only one entry per release series, following
    what every comparable project does — Node.js hosts every patch and lists
    none of them. This page is where the rest stay discoverable, grouped by
    major series the way Docusaurus groups its own `/versions` page.

    Written as a self-contained page with inlined styling rather than as part of
    a VitePress build: it lives at the language root, above every version, so it
    cannot borrow one version's assets without going stale when that version is
    replaced.
    """
    channels = [
        entry
        for entry in manifest.get("versions", [])
        if entry.get("kind") == "channel" or entry.get("key") in {"latest", "stable"}
    ]
    stable_key = manifest.get("stable")

    sections = []

    if channels:
        items = "\n".join(render_version_item(entry, stable_key) for entry in channels)
        sections.append(f"<h2>Current documentation</h2>\n<ul>\n{items}\n</ul>")

    for series, entries in release_groups(manifest):
        items = "\n".join(render_version_item(entry, stable_key) for entry in entries)
        heading = html.escape(series)
        sections.append(f"<h2>{heading} releases</h2>\n<ul>\n{items}\n</ul>")

    body = "\n".join(sections) or '<p class="lede">No versions published yet.</p>'
    root = f"/{html.escape(language)}/"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SQLFluff documentation versions</title>
<meta name="robots" content="noindex, follow">
<style>{VERSIONS_PAGE_STYLE}</style>
</head>
<body>
<h1>SQLFluff documentation versions</h1>
<p class="lede">
Every published version of the SQLFluff documentation. Released versions are
frozen at the point they were published and are not updated.
</p>
{body}
<footer>
<a href="{root}">Back to the current documentation</a>
</footer>
</body>
</html>
"""


def publish_not_found_page(
    dist: Path, output_dir: Path, language: str, manifest: dict[str, Any]
) -> None:
    """Publish the site-wide 404 page, taken from the default channel.

    Netlify only serves a `404.html` from the publish root. It does not fall back
    to one inside a subdirectory, so the VitePress 404 page each version builds
    was never reached — every miss on the beta site, including inside
    `/en/latest/`, returned Netlify's own generic page.

    Copied from a real build rather than written from scratch, which keeps it
    styled like the rest of the site for free.

    Taken from the default channel in the assembled tree rather than from the
    build being published, so it does not depend on which channels a given run
    happens to assemble. A prerelease publishes only itself — the workflow skips
    `stable` for prereleases — and the site's 404 page should not become a
    prerelease's, complete with a home link into it.

    When that channel has no 404 page of its own, an existing root page is left
    alone rather than replaced by this build's. Otherwise the guarantee above
    would hold only until some release happened to be published while the
    default channel was missing one, which is the situation this is here to
    prevent.

    This build is used only to bootstrap a tree that has no root page at all.
    There the mismatch cannot arise: if this is the only version published, its
    404 page names the only documentation there is. And when neither has one —
    the Sphinx case — nothing is written, so archiving a version cannot take the
    site's 404 page away.
    """
    channel_page = output_dir / language / default_channel(manifest) / "404.html"
    root_page = output_dir / "404.html"

    if channel_page.is_file():
        shutil.copy2(channel_page, root_page)
        return

    if root_page.exists() or not (dist / "404.html").is_file():
        return

    shutil.copy2(dist / "404.html", root_page)


def publish_shared_assets(shared_dir: Path, language_dir: Path) -> None:
    """Copy the shared runtime assets to the language root.

    Copied on every publish, not once. Archived versions load the picker from
    `/en/shared/` precisely so that a fix reaches them without a rebuild, which
    only holds if the newest copy is republished each time anything is.
    """
    if not shared_dir.is_dir():
        return

    target = language_dir / "shared"

    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(shared_dir, target)


def assemble_site(
    dist: Path,
    output_dir: Path,
    language: str,
    channel: str,
    title: str,
    kind: str,
    builder: str = "vitepress",
    prerelease: bool = False,
    unlisted: bool = False,
    published_at: str | None = None,
    stable_release: str | None = None,
    shared_dir: Path = SHARED_ASSETS,
    redirects: Path | None = None,
    allow_missing_redirect_targets: bool = False,
) -> None:
    """Merge one built docs channel into the assembled site tree."""
    if not dist.is_dir():
        raise FileNotFoundError(f"Build directory not found: {dist}")

    assert_safe_segment(language, "language")
    assert_safe_segment(channel, "channel")

    language_dir = output_dir / language
    target_dir = language_dir / channel
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        shutil.rmtree(target_dir)

    shutil.copytree(dist, target_dir)

    permalinks = load_redirect_map(redirects) if redirects else {}

    # Checked against the build that owns these permalinks. A Sphinx archive has
    # its own, as real pages, and lays its content out differently.
    if permalinks and builder == "vitepress":
        resolve_redirect_targets(dist, permalinks, allow_missing_redirect_targets)

    manifest_path = language_dir / "versions.json"
    manifest = load_manifest(manifest_path)
    manifest = upsert_manifest_entry(
        manifest,
        language=language,
        channel=channel,
        title=title,
        kind=kind,
        builder=builder,
        prerelease=prerelease,
        unlisted=unlisted,
        published_at=published_at,
        stable_release=stable_release,
    )
    write_text(manifest_path, json.dumps(manifest, indent=2))
    write_text(language_dir / "versions.html", build_versions_page(language, manifest))
    publish_shared_assets(shared_dir, language_dir)
    publish_not_found_page(dist, output_dir, language, manifest)
    write_text(
        output_dir / "_redirects", build_redirects(language, manifest, permalinks)
    )
    write_text(output_dir / "_headers", build_global_headers(language))


def main() -> int:
    """Main entry point."""
    args = parse_args()
    assemble_site(
        dist=args.dist,
        output_dir=args.output_dir,
        language=args.language.strip("/"),
        channel=args.channel.strip("/"),
        title=args.title
        or ("Development" if args.channel == "latest" else args.channel),
        kind=args.kind,
        builder=args.builder,
        prerelease=args.prerelease,
        unlisted=args.unlisted,
        published_at=args.published_at,
        stable_release=args.stable_release,
        shared_dir=args.shared_dir,
        redirects=args.redirects,
        allow_missing_redirect_targets=args.allow_missing_redirect_targets,
    )
    print(f"Assembled site written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
