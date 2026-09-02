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
        "builder": "vitepress",
        "prerelease": False,
        "unlisted": False,
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
        # Parsing drops `.` components, so these look like a single segment
        # afterwards while still naming a different directory.
        ".",
        "./foo",
        "foo/.",
        "a/",
        # Rooted without being absolute on Windows, which would put the delete
        # at the drive root.
        "\\",
        "/",
        "back\\slash",
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
            dist=dist,
            output_dir=tmp_path / "site",
            language="en",
            channel="../../outside",
            title="evil",
            kind="release",
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


def _keys_in_order(module, *keys: str) -> list[str]:
    entries = [{"key": key} for key in keys]
    entries.sort(key=module.version_sort_key)
    return [entry["key"] for entry in entries]


def test_channels_sort_before_releases(assemble_site):
    """The picker shows the moving channels first, then the pinned releases."""
    assert _keys_in_order(assemble_site, "3.4.2", "stable", "latest") == [
        "latest",
        "stable",
        "3.4.2",
    ]


def test_releases_sort_newest_first(assemble_site):
    """Descending version order, which the stale notice reads as newest-first."""
    assert _keys_in_order(assemble_site, "1.4.5", "3.4.2", "10.0.0", "3.10.0") == [
        "10.0.0",
        "3.10.0",
        "3.4.2",
        "1.4.5",
    ]


def test_post_release_sorts_above_the_release_it_follows(assemble_site):
    """`4.0.1.post1` is newer than `4.0.1`, and older than `4.1.0`.

    It used to fall into the non-numeric bucket below every release, including
    `0.2.4` — which also told the stale notice that every other release was
    newer than the newest one.
    """
    assert _keys_in_order(assemble_site, "4.0.1", "4.1.0", "4.0.1.post1", "4.0.2") == [
        "4.1.0",
        "4.0.2",
        "4.0.1.post1",
        "4.0.1",
    ]


def test_prereleases_sort_below_their_own_release(assemble_site):
    """`4.0.0a1` leads up to `4.0.0`, so it is older than it.

    `0.7.0a8` and `0.4.0a1` are real tags here, and both used to land in the
    string bucket at the bottom of the list.
    """
    assert _keys_in_order(
        assemble_site, "4.0.0", "4.0.0a1", "4.0.0a10", "4.0.0a2", "3.9.9"
    ) == ["4.0.0", "4.0.0a10", "4.0.0a2", "4.0.0a1", "3.9.9"]


def test_shorter_versions_sort_as_if_padded(assemble_site):
    """`3.4` names the same release as `3.4.0`, so it sorts with it."""
    assert _keys_in_order(assemble_site, "3.4", "3.5.0", "3.3.9") == [
        "3.5.0",
        "3.4",
        "3.3.9",
    ]


def test_unparseable_keys_sort_last(assemble_site):
    """A key nobody can order goes somewhere predictable rather than guessed."""
    assert _keys_in_order(assemble_site, "0.2.4", "nightly", "latest") == [
        "latest",
        "0.2.4",
        "nightly",
    ]


def test_builder_is_recorded_on_the_entry(assemble_site):
    """The picker drops the page path when switching across builders."""
    manifest = assemble_site.default_manifest()

    result = _upsert(assemble_site, manifest, builder="sphinx")

    assert _entry(result, "3.4.1")["builder"] == "sphinx"


def test_entries_are_listed_by_default(assemble_site):
    """A version is offered in the picker unless it is published unlisted."""
    manifest = assemble_site.default_manifest()

    result = _upsert(assemble_site, manifest)

    assert _entry(result, "3.4.1")["listed"] is True


def test_unlisted_entries_are_flagged(assemble_site):
    """An unlisted version stays published; the picker just does not offer it."""
    manifest = assemble_site.default_manifest()

    result = _upsert(assemble_site, manifest, unlisted=True)

    entry = _entry(result, "3.4.1")

    assert entry["listed"] is False
    assert entry["path"] == "/en/3.4.1/"


def _dist(tmp_path: Path, name: str = "dist") -> Path:
    dist = tmp_path / name
    dist.mkdir()
    (dist / "index.html").write_text("<html></html>", encoding="utf-8")
    return dist


def test_shared_assets_are_republished_every_run(assemble_site, tmp_path):
    """Archived versions load the picker from here, so it must stay current.

    An archived Sphinx build is produced once and frozen. It picks up picker
    changes only because these assets live above every version and are rewritten
    by whichever publish ran last.
    """
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "version-picker.js").write_text("// v1", encoding="utf-8")

    site = tmp_path / "site"
    published = site / "en" / "shared" / "version-picker.js"

    assemble_site.assemble_site(
        dist=_dist(tmp_path),
        output_dir=site,
        language="en",
        channel="latest",
        title="Development",
        kind="channel",
        shared_dir=shared,
    )

    assert published.read_text(encoding="utf-8") == "// v1"

    (shared / "version-picker.js").write_text("// v2", encoding="utf-8")
    assemble_site.assemble_site(
        dist=_dist(tmp_path, "dist-2"),
        output_dir=site,
        language="en",
        channel="3.4.2",
        title="3.4.2",
        kind="release",
        builder="sphinx",
        shared_dir=shared,
    )

    assert published.read_text(encoding="utf-8") == "// v2"


def test_versions_page_lists_unlisted_versions(assemble_site, tmp_path):
    """The archive page is where the versions the picker omits stay reachable."""
    site = tmp_path / "site"

    for channel, unlisted in (("3.4.2", False), ("3.4.1", True)):
        assemble_site.assemble_site(
            dist=_dist(tmp_path, f"dist-{channel}"),
            output_dir=site,
            language="en",
            channel=channel,
            title=channel,
            kind="release",
            builder="sphinx",
            unlisted=unlisted,
            shared_dir=tmp_path / "absent",
        )

    page = (site / "en" / "versions.html").read_text(encoding="utf-8")

    assert 'href="/en/3.4.2/"' in page
    assert 'href="/en/3.4.1/"' in page
    assert "3.x releases" in page


def test_versions_page_groups_releases_by_major(assemble_site):
    """Grouped by generation, following how Docusaurus groups its own."""
    manifest = assemble_site.default_manifest()
    manifest = _upsert(assemble_site, manifest, channel="4.1.0", title="4.1.0")
    manifest = _upsert(assemble_site, manifest, channel="3.4.2", title="3.4.2")
    manifest = _upsert(
        assemble_site,
        manifest,
        channel="latest",
        title="Development",
        kind="channel",
    )

    groups = assemble_site.release_groups(manifest)

    assert [series for series, _ in groups] == ["4.x", "3.x"]
    assert [entry["key"] for entry in groups[0][1]] == ["4.1.0"]


def test_headers_do_not_cache_shared_assets_immutably(assemble_site):
    """The assets have fixed filenames, so a long cache would freeze the picker."""
    headers = assemble_site.build_global_headers("en")

    shared = headers.split("/en/shared/*")[1]

    assert "must-revalidate" in shared
    assert "immutable" not in shared


def test_the_404_page_is_published_at_the_site_root(assemble_site, tmp_path):
    """Netlify only serves a 404 page from the publish root.

    It does not fall back to one inside a subdirectory, so the 404 page each
    VitePress version builds was never reached: every miss on the beta site,
    including inside `/en/latest/`, returned Netlify's own generic page.
    """
    dist = _dist(tmp_path)
    (dist / "404.html").write_text("<html>SQLFluff 404</html>", encoding="utf-8")

    site = tmp_path / "site"
    assemble_site.assemble_site(
        dist=dist,
        output_dir=site,
        language="en",
        channel="latest",
        title="Development",
        kind="channel",
        shared_dir=tmp_path / "absent",
    )

    assert (site / "404.html").read_text(
        encoding="utf-8"
    ) == "<html>SQLFluff 404</html>"


def test_a_build_without_a_404_page_leaves_the_existing_one(assemble_site, tmp_path):
    """Sphinx builds have no 404 page, and archiving one must not remove ours."""
    site = tmp_path / "site"

    vitepress = _dist(tmp_path, "vitepress")
    (vitepress / "404.html").write_text("<html>SQLFluff 404</html>", encoding="utf-8")

    assemble_site.assemble_site(
        dist=vitepress,
        output_dir=site,
        language="en",
        channel="latest",
        title="Development",
        kind="channel",
        shared_dir=tmp_path / "absent",
    )
    assemble_site.assemble_site(
        dist=_dist(tmp_path, "sphinx"),
        output_dir=site,
        language="en",
        channel="3.4.2",
        title="3.4.2",
        kind="release",
        builder="sphinx",
        shared_dir=tmp_path / "absent",
    )

    assert (site / "404.html").read_text(
        encoding="utf-8"
    ) == "<html>SQLFluff 404</html>"


def test_prerelease_stages_sort_in_pep440_order(assemble_site):
    """`a` before `b` before `rc`, rather than all three on their number alone.

    Only `aN` has ever been tagged here, so this was latent — but the manifest's
    ordering decides which release readers are warned about.
    """
    assert _keys_in_order(assemble_site, "4.0.0", "4.0.0a2", "4.0.0b1", "4.0.0rc1") == [
        "4.0.0",
        "4.0.0rc1",
        "4.0.0b1",
        "4.0.0a2",
    ]


def test_the_404_page_comes_from_the_default_channel(assemble_site, tmp_path):
    """Not from whichever build a given run happens to assemble.

    A prerelease publishes only itself — the workflow skips `stable` for
    prereleases — so taking the page from the build in hand would make the
    site's 404 a prerelease's, complete with a home link into it.
    """
    site = tmp_path / "site"

    latest = _dist(tmp_path, "latest")
    (latest / "404.html").write_text("<html>latest 404</html>", encoding="utf-8")

    assemble_site.assemble_site(
        dist=latest,
        output_dir=site,
        language="en",
        channel="latest",
        title="Development",
        kind="channel",
        shared_dir=tmp_path / "absent",
    )

    prerelease = _dist(tmp_path, "prerelease")
    (prerelease / "404.html").write_text("<html>4.4.0a1 404</html>", encoding="utf-8")

    assemble_site.assemble_site(
        dist=prerelease,
        output_dir=site,
        language="en",
        channel="4.4.0a1",
        title="4.4.0a1",
        kind="release",
        prerelease=True,
        shared_dir=tmp_path / "absent",
    )

    assert (site / "404.html").read_text(encoding="utf-8") == "<html>latest 404</html>"


def test_the_404_page_tracks_the_default_channel_when_it_is_rebuilt(
    assemble_site, tmp_path
):
    """Rebuilding the default channel refreshes the root copy with it.

    The copy references that channel's fingerprinted assets, and the channel
    directory is deleted and rewritten on every publish, so the two have to move
    together.
    """
    site = tmp_path / "site"

    for body in ("<html>first</html>", "<html>second</html>"):
        dist = _dist(tmp_path, f"dist-{len(body)}{body[6]}")
        (dist / "404.html").write_text(body, encoding="utf-8")
        assemble_site.assemble_site(
            dist=dist,
            output_dir=site,
            language="en",
            channel="latest",
            title="Development",
            kind="channel",
            shared_dir=tmp_path / "absent",
        )

    assert (site / "404.html").read_text(encoding="utf-8") == "<html>second</html>"


def _publish_default_channel_without_a_404(module, tmp_path, site) -> None:
    """Publish `latest` from a build that has no 404 page of its own."""
    module.assemble_site(
        dist=_dist(tmp_path, "latest-no-404"),
        output_dir=site,
        language="en",
        channel="latest",
        title="Development",
        kind="channel",
        shared_dir=tmp_path / "absent",
    )


def _publish_prerelease_with_a_404(module, tmp_path, site) -> None:
    """Publish a prerelease from a build that does have one."""
    release = _dist(tmp_path, "prerelease-with-404")
    (release / "404.html").write_text("<html>4.4.0a1 404</html>", encoding="utf-8")

    module.assemble_site(
        dist=release,
        output_dir=site,
        language="en",
        channel="4.4.0a1",
        title="4.4.0a1",
        kind="release",
        prerelease=True,
        shared_dir=tmp_path / "absent",
    )


def test_an_existing_404_page_is_not_downgraded(assemble_site, tmp_path):
    """A release must not claim the root 404 when the default channel lacks one.

    Otherwise taking the page from the default channel would hold only until some
    release happened to be published while that channel had no 404 page — which
    is the situation it is there to prevent.
    """
    site = tmp_path / "site"

    _publish_default_channel_without_a_404(assemble_site, tmp_path, site)
    (site / "404.html").write_text("<html>existing</html>", encoding="utf-8")
    _publish_prerelease_with_a_404(assemble_site, tmp_path, site)

    assert (site / "404.html").read_text(encoding="utf-8") == "<html>existing</html>"


def test_a_tree_with_no_404_page_is_bootstrapped_from_the_build(
    assemble_site, tmp_path
):
    """With no root page to protect, this build's is better than none.

    Reached when the default channel has no 404 page and the site has none
    either, so there is nothing better available and nothing to lose.
    """
    site = tmp_path / "site"

    _publish_default_channel_without_a_404(assemble_site, tmp_path, site)
    assert not (site / "404.html").exists(), "premise of the test"

    _publish_prerelease_with_a_404(assemble_site, tmp_path, site)

    assert (site / "404.html").read_text(encoding="utf-8") == "<html>4.4.0a1 404</html>"
