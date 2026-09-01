"""Tests for the assembled-site smoke check.

This is the last thing to run before a tree leaves the runner for R2 and
Netlify, so what it vouches for has to be inside the tree it was handed.

The script lives outside the package, so it is loaded by path rather than
imported; its filename is not a valid module name.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parent.parent
SMOKE_CHECK = REPO_ROOT / "docsv" / "scripts" / "smoke-check-assembled-site.py"


def _load_smoke_check() -> ModuleType:
    spec = importlib.util.spec_from_file_location("smoke_check", SMOKE_CHECK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def smoke_check() -> ModuleType:
    """Load the smoke check once for the module."""
    return _load_smoke_check()


def test_a_suffixless_path_resolves_to_its_html_file(smoke_check, tmp_path):
    """Netlify serves `foo.html` for `/foo`, and the permalink rules rely on it.

    Their destinations are suffix-less so that one rule can serve versions whose
    builds put the page in a different file.
    """
    (tmp_path / "en" / "latest" / "configuration").mkdir(parents=True)
    (tmp_path / "en" / "latest" / "configuration" / "layout.html").write_text(
        "<html></html>", encoding="utf-8"
    )

    smoke_check.assert_path_exists(
        tmp_path, "/en/latest/configuration/layout", "permalink target"
    )


def test_a_symlinked_html_file_outside_the_tree_is_rejected(smoke_check, tmp_path):
    """The `.html` fallback must not escape the tree it is checking.

    `resolve()` follows symlinks, so without re-checking containment after the
    suffix is appended, a link at the `.html` name would let the check vouch for
    a page the deployed site does not have.
    """
    site = tmp_path / "site"
    (site / "en" / "latest").mkdir(parents=True)

    outside = tmp_path / "outside.html"
    outside.write_text("<html>not published</html>", encoding="utf-8")
    (site / "en" / "latest" / "escape.html").symlink_to(outside)

    with pytest.raises(ValueError, match="escapes the site directory"):
        smoke_check.assert_path_exists(site, "/en/latest/escape", "permalink target")


def test_a_missing_page_is_still_reported(smoke_check, tmp_path):
    """The suffix fallback must not turn a missing page into a passing check."""
    (tmp_path / "en" / "latest").mkdir(parents=True)

    with pytest.raises(FileNotFoundError):
        smoke_check.assert_path_exists(
            tmp_path, "/en/latest/absent", "permalink target"
        )


@pytest.mark.parametrize("url_path", ["/en/../../outside", "/", ""])
def test_unsafe_paths_are_rejected(smoke_check, tmp_path, url_path):
    """A manifest is only as trustworthy as whatever produced it."""
    with pytest.raises(ValueError):
        smoke_check.assert_path_exists(tmp_path, url_path, "version index")
