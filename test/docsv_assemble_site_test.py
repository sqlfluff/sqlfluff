"""Tests for the versioned docs site assembly script.

These cover the manifest contract that the published version picker depends on.
The script lives outside the package, so it is loaded by path rather than
imported; its filename is not a valid module name.
"""

import importlib.util
from pathlib import Path, PureWindowsPath
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


@pytest.mark.parametrize(
    "channel",
    [
        "..",
        "../outside",
        "en/../../outside",
        "a/b",
        "/absolute",
        "",
        " padded ",
    ],
)
def test_unsafe_channels_are_rejected(assemble_site, channel):
    """A channel is a directory name which gets deleted and rewritten.

    A manual publish takes it from an operator-supplied version, so a separator
    or a `..` would move that delete outside the assembled site.
    """
    with pytest.raises(ValueError):
        assemble_site.assert_safe_segment(channel, "channel")


def test_drive_qualified_channels_are_rejected(assemble_site):
    """`C:foo` is neither absolute nor separated, but does relocate a path.

    Checked with the Windows flavour explicitly, since the value is harmless on
    the POSIX runner that publishes today but not on a maintainer's Windows
    machine, where these scripts have been run before.
    """
    assert PureWindowsPath("C:foo").is_absolute() is False, "premise of the test"
    assert PureWindowsPath("C:foo").drive == "C:"

    with pytest.raises(ValueError):
        assemble_site.assert_safe_segment("C:foo", "channel")


@pytest.mark.parametrize(
    "channel",
    ["latest", "stable", "3.4.2", "4.0.0a1", "4.0.1.post1", "1.2.3-rc.1"],
)
def test_real_channels_are_accepted(assemble_site, channel):
    """The names actually published must not be caught by the guard.

    `4.0.0a1` and `4.0.1.post1` are both real tags in this repository.
    """
    assemble_site.assert_safe_segment(channel, "channel")


def test_assemble_site_refuses_to_escape_the_output_dir(assemble_site, tmp_path):
    """The guard is wired into the destructive path, not just available."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html></html>", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("sentinel", encoding="utf-8")

    with pytest.raises(ValueError):
        assemble_site.assemble_site(
            vitepress_dist=dist,
            output_dir=tmp_path / "site",
            language="en",
            channel="../../outside",
            title="evil",
            kind="release",
            prerelease=False,
            published_at=None,
            stable_release=None,
        )

    assert (outside / "keep.txt").is_file(), (
        "content outside the output dir was removed"
    )


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
