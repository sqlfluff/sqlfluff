#!/usr/bin/env python3
"""Backfill final release documentation into an assembled beta site.

Read the Docs already has frozen Sphinx builds for most old releases. Mirror
those builds to preserve their original content. Releases which Read the Docs
never built are rebuilt from their tags with Sphinx. The first VitePress release
actually published through the versioned pipeline was 4.2.2, so older releases
use Sphinx even though the original hosting proposal named 4.2.0 as its cutoff.
"""

from __future__ import annotations

import argparse
import ast
import html.parser
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import deque
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
RELEASE = re.compile(
    r"^(?P<major>[2-9]\d*)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:\.post(?P<post>\d+))?$"
)
ASSET_URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)", re.IGNORECASE)
RTD_HOST = "docs.sqlfluff.com"
MIN_HTML_PAGES = 15


def run(*args: str, cwd: Path = REPO) -> None:
    """Run a command, failing the backfill on a nonzero exit status."""
    subprocess.run(args, cwd=cwd, check=True)


def output(*args: str, cwd: Path = REPO) -> str:
    """Capture a command's UTF-8 output."""
    return subprocess.check_output(args, cwd=cwd, text=True, encoding="utf-8")


def release_key(tag: str) -> tuple[int, int, int, int]:
    """Sort final releases, including post releases, without prereleases."""
    match = RELEASE.fullmatch(tag)
    if not match:
        raise ValueError(f"Not a final release tag: {tag}")
    return (
        int(match["major"]),
        int(match["minor"]),
        int(match["patch"]),
        int(match["post"] or 0),
    )


def final_releases(major: int) -> list[str]:
    """Return final release tags for one major series, oldest first."""
    return sorted(
        (
            tag
            for tag in output("git", "tag", "--list").splitlines()
            if RELEASE.fullmatch(tag) and release_key(tag)[0] == major
        ),
        key=release_key,
    )


def redirect_pages(tag: str) -> list[str]:
    """Find Sphinx redirect pages that a normal link crawl would miss."""
    source = output("git", "show", f"{tag}:docs/source/conf.py")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "redirects"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        pages = []
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                pages.append(key.value + ".html")
        return pages
    return []


class Links(html.parser.HTMLParser):
    """Collect local page and asset references from served Sphinx HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record links and assets from an HTML start tag."""
        for key, value in attrs:
            if value is None:
                continue
            if key in {"href", "src", "data-src"}:
                self.urls.append(value)
            elif key == "srcset":
                self.urls.extend(
                    item.split()[0] for item in value.split(",") if item.strip()
                )


class RTDMirror:
    """Copy one published Read the Docs version into a standalone directory."""

    def __init__(self, tag: str, destination: Path) -> None:
        self.base = f"https://{RTD_HOST}/en/{tag}/"
        self.prefix = f"/en/{tag}/"
        self.destination = destination
        self.todo: deque[str] = deque()
        self.seen: set[str] = set()
        self.missing: list[str] = []
        self.html_pages = 0

    def add(self, current: str, link: str) -> None:
        """Queue a link only when it remains inside this version."""
        url = urllib.parse.urljoin(current, link)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != RTD_HOST:
            return
        path = urllib.parse.unquote(parsed.path)
        if not path.startswith(self.prefix):
            return
        relative = path[len(self.prefix) :]
        if not relative or path.endswith("/"):
            relative += "index.html"
        if any(part in {".", ".."} for part in Path(relative).parts):
            return
        if relative not in self.seen:
            self.todo.append(relative)
            self.seen.add(relative)

    def fetch(self, relative: str) -> None:
        """Fetch one file and discover its local dependencies."""
        url = urllib.parse.urljoin(self.base, relative)
        request = urllib.request.Request(
            url, headers={"User-Agent": "SQLFluff-docs-backfill/1.0"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if not response.url.startswith(self.base):
                    raise ValueError(
                        f"Historical URL escaped its version: {url} -> {response.url}"
                    )
                body = response.read()
                content_type = response.headers.get_content_type()
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and relative != "index.html":
                self.missing.append(relative)
                return
            raise

        target = self.destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)

        if content_type == "text/html":
            self.html_pages += 1
            links = Links()
            links.feed(body.decode("utf-8", errors="replace"))
            for link in links.urls:
                self.add(url, link)
        elif content_type == "text/css":
            for link in ASSET_URL.findall(body.decode("utf-8", errors="replace")):
                self.add(url, link)

    def mirror(self, redirects: list[str]) -> int:
        """Mirror reachable pages, declared redirects, and Sphinx search assets."""
        self.add(self.base, "index.html")
        for path in ("searchindex.js", "objects.inv", *redirects):
            self.add(self.base, path)
        while self.todo:
            self.fetch(self.todo.popleft())
        if self.html_pages < MIN_HTML_PAGES:
            raise ValueError(
                f"Only {self.html_pages} HTML pages mirrored from {self.base}"
            )
        if self.missing:
            print(
                f"Source site returned 404 for {len(self.missing)} files under "
                f"{self.base}: {', '.join(self.missing[:10])}",
                flush=True,
            )
        return self.html_pages


def build_sphinx(tag: str, source: Path, dist: Path) -> None:
    """Build a release absent from Read the Docs using its tagged source."""
    archive = source.parent / f"{tag}.zip"
    run("git", "archive", "--format=zip", "--output", str(archive), tag)
    with zipfile.ZipFile(archive) as snapshot:
        snapshot.extractall(source)
    # Several 4.x tags accidentally read a TOML table with ConfigParser's API,
    # making the rendered release string literally "stable_version". Correct the
    # temporary source copy so a rebuilt archive has its real version identity.
    conf = source / "docs" / "source" / "conf.py"
    contents = conf.read_text(encoding="utf-8")
    old = 'stable_version = config.get("tool.sqlfluff_docs", "stable_version")'
    if old in contents:
        conf.write_text(
            contents.replace(old, f'stable_version = "{tag}"'), encoding="utf-8"
        )
    run(
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        str(source),
        "-r",
        str(source / "docs" / "requirements.txt"),
    )
    run(sys.executable, "generate-auto-docs.py", cwd=source / "docs")
    run(
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "html",
        "--keep-going",
        str(source / "docs" / "source"),
        str(dist),
        cwd=source / "docs",
    )


def load_script(name: str) -> Any:
    """Load an existing hyphenated docs script without duplicating its logic."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fix_release_identity(dist: Path, tag: str) -> None:
    """Correct the literal placeholder in historical Sphinx page titles."""
    for page in dist.rglob("*.html"):
        original = page.read_text(encoding="utf-8", errors="replace")
        updated = original.replace(
            "SQLFluff stable_version documentation", f"SQLFluff {tag} documentation"
        )
        if updated != original:
            page.write_text(updated, encoding="utf-8")


def backfill(tag: str, site_dir: Path) -> None:
    """Build or mirror, inject the picker, and assemble one Sphinx release."""
    with tempfile.TemporaryDirectory(prefix=f"sqlfluff-docs-{tag}-") as temp:
        work = Path(temp)
        dist = work / "html"
        mirror = RTDMirror(tag, dist)
        try:
            count = mirror.mirror(redirect_pages(tag))
            print(f"Mirrored {count} Sphinx HTML pages for {tag}", flush=True)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            shutil.rmtree(dist, ignore_errors=True)
            build_sphinx(tag, work / "source", dist)
            print(f"Built Sphinx docs from tag {tag}", flush=True)

        fix_release_identity(dist, tag)
        injector = load_script("inject-shared-picker")
        injector.inject(dist, "/en/shared/")
        assembler = load_script("assemble-site")
        assembler.assemble_site(
            dist=dist,
            output_dir=site_dir,
            language="en",
            channel=tag,
            title=tag,
            kind="release",
            builder="sphinx",
            unlisted=True,
            redirects=assembler.DEFAULT_REDIRECTS,
        )


def curate_picker(site_dir: Path, major: int, newest: str) -> None:
    """List one final release per major series in the picker."""
    assembler = load_script("assemble-site")
    manifest_path = site_dir / "en" / "versions.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["versions"]:
        tag = str(entry.get("key", ""))
        if entry.get("kind") == "release" and RELEASE.fullmatch(tag):
            if release_key(tag)[0] == major:
                entry["listed"] = tag == newest
    assembler.write_text(manifest_path, json.dumps(manifest, indent=2))
    assembler.write_text(
        site_dir / "en" / "versions.html", assembler.build_versions_page("en", manifest)
    )


def main() -> int:
    """Backfill absent versions in one major series, then smoke-check the site."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, required=True)
    parser.add_argument("--major", type=int, choices=(2, 3, 4), required=True)
    args = parser.parse_args()

    site_dir = args.site_dir.resolve()
    manifest_path = site_dir / "en" / "versions.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            "Download the existing assembled site before backfilling"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    published = {entry["key"] for entry in manifest.get("versions", [])}

    versions = final_releases(args.major)
    if not versions:
        raise ValueError(f"No final release tags found for major {args.major}")

    for tag in versions:
        if release_key(tag) >= release_key("4.2.2"):
            if (
                tag not in published
                or not (site_dir / "en" / tag / "index.html").is_file()
            ):
                raise ValueError(
                    f"VitePress release {tag} is missing; publish it through publish-docs.yaml"
                )
            continue
        if tag in published and (site_dir / "en" / tag / "index.html").is_file():
            print(f"Already published: {tag}", flush=True)
            continue
        print(f"Backfilling {tag}", flush=True)
        backfill(tag, site_dir)
        published.add(tag)

    curate_picker(site_dir, args.major, versions[-1])
    smoke = load_script("smoke-check-assembled-site")
    smoke.smoke_check(site_dir, "en")
    print(f"Backfill complete for major {args.major}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
