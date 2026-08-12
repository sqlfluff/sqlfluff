"""Tests for the versioned docs site assembly script.

These cover the manifest contract that the published version picker depends on.
The script lives outside the package, so it is loaded by path rather than
imported; its filename is not a valid module name.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parent.parent
ASSEMBLE_SITE = REPO_ROOT / "docsv" / "scripts" / "assemble-site.py"


def _load_assemble_site() -> ModuleType:
    spec = importlib.util.spec_from_file_location("assemble_site", ASSEMBLE_SITE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def assemble_site() -> ModuleType:
    """Load the assembly script once for the module."""
    return _load_assemble_site()


def _upsert(module: ModuleType, manifest: dict, **overrides) -> dict:
    kwargs = {
        "language": "en",
        "channel": "3.4.1",
        "title": "3.4.1",
        "kind": "release",
        "prerelease": False,
        "published_at": None,
        "stable_release": None,
    }
    kwargs.update(overrides)
    return module.upsert_manifest_entry(manifest, **kwargs)


def _entry(manifest: dict, key: str) -> dict:
    return next(entry for entry in manifest["versions"] if entry["key"] == key)


def test_published_at_is_recorded_when_supplied(assemble_site):
    """An explicit date is written onto the entry."""
    manifest = assemble_site.default_manifest()

    result = _upsert(assemble_site, manifest, published_at="2026-06-02")

    assert _entry(result, "3.4.1")["published_at"] == "2026-06-02"


def test_published_at_is_preserved_when_omitted_on_rebuild(assemble_site):
    """Rebuilding a release without a date keeps the one already published.

    The entry is rebuilt from scratch on every run, so without this the date
    would be erased by any manual rebuild which did not repeat it.
    """
    manifest = assemble_site.default_manifest()
    manifest = _upsert(assemble_site, manifest, published_at="2026-06-02")

    rebuilt = _upsert(assemble_site, manifest, published_at=None)

    assert _entry(rebuilt, "3.4.1")["published_at"] == "2026-06-02"


def test_published_at_is_overwritten_when_supplied_on_rebuild(assemble_site):
    """An explicit date wins over the existing one."""
    manifest = assemble_site.default_manifest()
    manifest = _upsert(assemble_site, manifest, published_at="2026-06-02")

    rebuilt = _upsert(assemble_site, manifest, published_at="2026-06-09")

    assert _entry(rebuilt, "3.4.1")["published_at"] == "2026-06-09"


def test_published_at_is_absent_for_a_new_release_without_one(assemble_site):
    """A release published with no date simply has no date."""
    manifest = assemble_site.default_manifest()

    result = _upsert(assemble_site, manifest, published_at=None)

    assert "published_at" not in _entry(result, "3.4.1")


def test_published_at_is_not_applied_to_channels(assemble_site):
    """Channels move, so a publication date would be meaningless on one."""
    manifest = assemble_site.default_manifest()

    result = _upsert(
        assemble_site,
        manifest,
        channel="latest",
        title="Latest",
        kind="channel",
        published_at="2026-06-02",
    )

    assert "published_at" not in _entry(result, "latest")


def test_rebuild_leaves_other_versions_untouched(assemble_site):
    """Only the rebuilt entry changes."""
    manifest = assemble_site.default_manifest()
    manifest = _upsert(assemble_site, manifest, published_at="2026-06-02")
    manifest = _upsert(
        assemble_site,
        manifest,
        channel="3.4.2",
        title="3.4.2",
        published_at="2026-07-14",
    )

    rebuilt = _upsert(assemble_site, manifest, published_at=None)

    assert _entry(rebuilt, "3.4.2")["published_at"] == "2026-07-14"
    assert _entry(rebuilt, "3.4.1")["published_at"] == "2026-06-02"
