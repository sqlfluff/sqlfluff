"""Tests for the versioned permalink redirect rules.

These cover the URLs SQLFluff itself emits. Every release from `2.0.0` onward
prints `.../perma/<name>.html` links from the CLI and from rule documentation, so
a reader following one arrives on the site cold — which is the case the
client-side redirect handling cannot serve, because the server answers `404`
before any JavaScript runs.

The script lives outside the package, so it is loaded by path rather than
imported; its filename is not a valid module name.
"""

import importlib.util
import json
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


@pytest.fixture
def dist(tmp_path: Path) -> Path:
    """A minimal built tree with the pages the permalinks point at."""
    root = tmp_path / "dist"

    for page in (
        "index.html",
        "configuration/layout.html",
        "configuration/index.html",
        "reference/rules/structure.html",
    ):
        path = root / page
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<html>page</html>", encoding="utf-8")

    return root


def _rules(module: ModuleType, redirects: dict[str, str]) -> list[str]:
    return module.build_permalink_rules("en", redirects)


def test_both_url_suffixes_are_covered(assemble_site):
    """The CLI emits `perma/layout.html`; a reader who trims it gets the other.

    Both are in the wild, and neither is a file in any published version, which
    is why a cold hit returned `404` regardless of what the client-side handler
    would have done with it.
    """
    rules = _rules(assemble_site, {"perma/layout": "configuration/layout"})

    assert rules == [
        "/en/:version/perma/layout /en/:version/configuration/layout 301",
        "/en/:version/perma/layout.html /en/:version/configuration/layout 301",
    ]


def test_rules_are_version_agnostic(assemble_site):
    """One rule per permalink, not one per permalink per version.

    Enumerating versions would add 204 rules a release and pass Netlify's
    recommended ceiling within a handful of them. It would also leave versions
    published before this existed unfixed, which a placeholder does not: their
    permalinks were never files, and rebuilding an old tag rebuilds it from
    source that does not know about them.
    """
    rules = _rules(assemble_site, {"perma/layout": "configuration/layout"})

    assert all(rule.count(":version") == 2 for rule in rules)


def test_rules_are_permanent(assemble_site):
    """A permalink is a promise, so it earns a 301 rather than a 302."""
    rules = _rules(assemble_site, {"perma/layout": "configuration/layout"})

    assert all(rule.endswith(" 301") for rule in rules)


def test_rules_are_not_forced(assemble_site):
    """A `!` would shadow the archived Sphinx versions' own permalink pages.

    Those pages are real files written by `sphinx-reredirects`, and they are
    correct for that version's page layout where these rules are not. Netlify
    serves an existing file in preference to an unforced rule.
    """
    rules = _rules(assemble_site, {"perma/layout": "configuration/layout"})

    assert not any("!" in rule for rule in rules)


def test_fragments_are_preserved(assemble_site):
    """Most rule permalinks point at a heading rather than at a page."""
    rules = _rules(assemble_site, {"perma/rule/ST01": "reference/rules/structure#st01"})

    assert rules[0] == (
        "/en/:version/perma/rule/ST01 /en/:version/reference/rules/structure#st01 301"
    )


def test_a_permalink_to_a_permalink_is_followed(assemble_site):
    """`internals` points at `perma/internals`, which points at the page.

    The client-side handler followed that chain by accident — each hop 404s and
    re-runs the handler — so it went unnoticed. Resolving it fully saves the
    reader a second round trip.
    """
    rules = _rules(
        assemble_site,
        {
            "internals": "perma/internals",
            "perma/internals": "reference/internals/index",
        },
    )

    assert "/en/:version/internals /en/:version/reference/internals/index 301" in rules
    assert not any("perma/internals 301" in rule for rule in rules)


def test_a_permalink_cycle_is_rejected(assemble_site):
    """Following it would loop; the reader's browser would too."""
    with pytest.raises(ValueError, match="does not terminate"):
        _rules(assemble_site, {"a": "b", "b": "a"})


def test_rules_follow_the_root_redirects(assemble_site):
    """Both sets live in one file, and the root rules stay first."""
    manifest = assemble_site.default_manifest()
    manifest["versions"] = [{"key": "latest"}]

    content = assemble_site.build_redirects(
        "en", manifest, {"perma/layout": "configuration/layout"}
    )
    lines = [line for line in content.splitlines() if line]

    assert lines[0] == "/ /en/latest/ 302"
    assert lines[3].startswith("/en/:version/perma/layout ")


def test_no_permalink_map_leaves_the_root_redirects_alone(assemble_site):
    """A publish which cannot find the map still produces a working site."""
    manifest = assemble_site.default_manifest()
    manifest["versions"] = [{"key": "latest"}]

    content = assemble_site.build_redirects("en", manifest, {})

    assert "perma" not in content
    assert "/ /en/latest/ 302" in content


def test_comment_keys_are_dropped(assemble_site, tmp_path):
    """`_comment` is the convention these config files use."""
    path = tmp_path / "redirects.json"
    path.write_text(
        json.dumps({"_comment": "notes", "perma/layout": "configuration/layout"}),
        encoding="utf-8",
    )

    assert assemble_site.load_redirect_map(path) == {
        "perma/layout": "configuration/layout"
    }


def test_a_missing_map_is_not_fatal(assemble_site, tmp_path):
    """The smoke check is the backstop; a publish should not die here."""
    assert assemble_site.load_redirect_map(tmp_path / "absent.json") == {}


def test_a_missing_target_fails_the_publish(assemble_site, dist):
    """A permalink to a page that no longer exists redirects a 404 to a 404.

    Better found in the publish that renamed the page than by a reader following
    a link printed by a released version of SQLFluff.
    """
    with pytest.raises(FileNotFoundError, match="no built page"):
        assemble_site.resolve_redirect_targets(
            dist, {"perma/gone": "configuration/removed"}
        )


def test_directory_targets_count_as_present(assemble_site, dist):
    """Which file a page became depends on the build's URL settings."""
    assemble_site.resolve_redirect_targets(
        dist, {"perma/configuration": "configuration/index"}
    )


def test_missing_targets_can_be_downgraded_to_a_warning(assemble_site, dist):
    """The escape hatch, for publishing with a known-stale permalink."""
    assemble_site.resolve_redirect_targets(
        dist, {"perma/gone": "configuration/removed"}, allow_missing=True
    )


def test_sphinx_builds_skip_target_validation(assemble_site, tmp_path):
    """An archive lays its pages out differently and has its own permalinks.

    Validating the VitePress map against a Sphinx tree would fail every archived
    version, since `configuration/layout.html` is `configuration/index.html`
    there.
    """
    sphinx_dist = tmp_path / "sphinx"
    sphinx_dist.mkdir()
    (sphinx_dist / "index.html").write_text("<html></html>", encoding="utf-8")
    (sphinx_dist / "perma").mkdir()
    (sphinx_dist / "perma" / "layout.html").write_text(
        "<html></html>", encoding="utf-8"
    )

    redirects = tmp_path / "redirects.json"
    redirects.write_text(
        json.dumps({"perma/layout": "configuration/layout"}), encoding="utf-8"
    )

    site = tmp_path / "site"
    assemble_site.assemble_site(
        dist=sphinx_dist,
        output_dir=site,
        language="en",
        channel="3.4.2",
        title="3.4.2",
        kind="release",
        builder="sphinx",
        shared_dir=tmp_path / "absent",
        redirects=redirects,
    )

    # The rules are still written: they are how the versions that have no
    # permalink pages of their own get served.
    assert "perma/layout" in (site / "_redirects").read_text(encoding="utf-8")


def test_every_shipped_permalink_resolves(assemble_site):
    """The real map must not accumulate permalinks to pages that no longer exist.

    Checked against the map rather than a built tree, which is not available
    here: this asserts the shape the generator relies on, so a malformed entry
    is caught by the test suite rather than by a docs publish.
    """
    redirects = assemble_site.load_redirect_map(assemble_site.DEFAULT_REDIRECTS)

    assert redirects, "redirects.json is empty"

    for key, target in redirects.items():
        assert not key.startswith("/"), f"{key} must be a relative page id"
        assert ".." not in key.split("/"), f"{key} must not traverse"

        path, _ = assemble_site.follow_chain(redirects, target)

        assert path, f"{key} has no target path"
        assert not path.startswith("/"), (
            f"{key} points at an absolute path, which would not survive a "
            f"change of base"
        )

    # Every rule is generated without raising, which is where a cycle surfaces.
    assert (
        len(assemble_site.build_permalink_rules("en", redirects)) == len(redirects) * 2
    )


@pytest.mark.parametrize(
    "target",
    [
        "",
        "   ",
        None,
        42,
        " configuration/layout",
        "configuration/layout ",
        "configuration/my layout",
    ],
)
def test_malformed_targets_are_rejected(assemble_site, tmp_path, target):
    """`_redirects` is space-delimited, so whitespace is not merely useless.

    A target of `"   "` produced `/en/:version/perma/x /en/:version/    301` — a
    rule that parses as something nobody wrote, pointing at the version root.
    """
    path = tmp_path / "redirects.json"
    path.write_text(json.dumps({"perma/layout": target}), encoding="utf-8")

    with pytest.raises(ValueError, match="Unusable permalinks"):
        assemble_site.load_redirect_map(path)


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        # `key.strip("/")` makes this the version root, so the rule would
        # redirect every version's home page to whatever the target is.
        ("", "empty permalink"),
        ("perma/my layout", "whitespace"),
        ("../escape", "`..` component"),
    ],
)
def test_malformed_keys_are_rejected(assemble_site, tmp_path, key, expected):
    """The source half of a rule is a request path too, not just the target."""
    path = tmp_path / "redirects.json"
    path.write_text(json.dumps({key: "configuration/layout"}), encoding="utf-8")

    with pytest.raises(ValueError, match=expected):
        assemble_site.load_redirect_map(path)


def test_a_dotdot_target_is_rejected(assemble_site, tmp_path):
    """Netlify normalises request paths, so such a rule silently never fires."""
    path = tmp_path / "redirects.json"
    path.write_text(json.dumps({"perma/x": "../escape"}), encoding="utf-8")

    with pytest.raises(ValueError, match="`..` component"):
        assemble_site.load_redirect_map(path)


def test_the_reason_an_entry_was_rejected_is_reported(assemble_site, tmp_path):
    """Whoever hits this needs to know which entry and why, not just that."""
    path = tmp_path / "redirects.json"
    path.write_text(
        json.dumps({"perma/good": "configuration/layout", "perma/bad": ""}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"'perma/bad': no target"):
        assemble_site.load_redirect_map(path)


def test_the_shipped_map_loads_cleanly(assemble_site):
    """The validation above must not reject the map actually published."""
    assert len(assemble_site.load_redirect_map(assemble_site.DEFAULT_REDIRECTS)) == 102
