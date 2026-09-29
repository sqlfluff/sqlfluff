"""Tests for controlled historical documentation backfills."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def backfill():
    """Load the backfill script, whose file name contains a hyphen."""
    path = Path(__file__).resolve().parents[1] / "docsv/scripts/backfill-docs.py"
    spec = importlib.util.spec_from_file_location("backfill_docs", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_final_release_selection_includes_post_releases(backfill):
    """Only final release tags belong in the historical archive."""
    assert backfill.release_key("4.0.1") < backfill.release_key("4.0.1.post1")
    assert backfill.release_key("4.0.1.post1") < backfill.release_key("4.0.2")
    for tag in ("2.0.0a1", "4.0.4a1", "4.2.0rc1", "1.4.0"):
        with pytest.raises(ValueError, match="Not a final release"):
            backfill.release_key(tag)


def test_mirror_stays_within_the_requested_version(backfill, tmp_path):
    """A mirrored page cannot pull another release or an external site in."""
    mirror = backfill.RTDMirror("2.0.0", tmp_path)
    mirror.add(mirror.base, "gettingstarted.html#install")
    mirror.add(mirror.base, "_static/alabaster.css")
    mirror.add(mirror.base, "../../stable/index.html")
    mirror.add(mirror.base, "https://example.com/asset.js")
    assert set(mirror.todo) == {"gettingstarted.html", "_static/alabaster.css"}


def test_historical_redirect_pages_are_discovered(backfill, monkeypatch):
    """The old redirect pages are not linked in the navigation crawl."""
    monkeypatch.setattr(
        backfill,
        "output",
        lambda *args: (
            'redirects = {"indentation": "layout.html", '
            '"architecture": "internals.html"}\n'
        ),
    )
    assert {"indentation.html", "architecture.html"}.issubset(
        set(backfill.redirect_pages("2.0.0"))
    )


def test_major_four_inventory_includes_only_final_releases(backfill, monkeypatch):
    """The backfill ignores prereleases and tags outside the chosen series."""
    monkeypatch.setattr(
        backfill,
        "output",
        lambda *args: "4.0.2\n4.0.4a1\n4.1.0\n4.2.1\n3.5.0\n",
    )
    tags = backfill.final_releases(4)
    assert tags == ["4.0.2", "4.1.0", "4.2.1"]


def test_historical_page_uses_its_actual_release_number(backfill, tmp_path):
    """Some published Sphinx builds contain a literal version placeholder."""
    page = tmp_path / "index.html"
    page.write_text(
        "<title>SQLFluff stable_version documentation</title>", encoding="utf-8"
    )

    backfill.fix_release_identity(tmp_path, "4.0.1.post1")

    assert "SQLFluff 4.0.1.post1 documentation" in page.read_text(encoding="utf-8")


def test_picker_lists_only_the_newest_release_in_a_backfilled_series(
    backfill, tmp_path
):
    """All patches stay on the archive page without filling the picker."""
    language = tmp_path / "en"
    language.mkdir()
    manifest = {
        "default": "latest",
        "versions": [
            {
                "key": tag,
                "title": tag,
                "path": f"/en/{tag}/",
                "kind": "release",
                "builder": "sphinx",
                "listed": True,
            }
            for tag in ("2.0.0", "2.3.5", "3.5.0")
        ],
    }
    (language / "versions.json").write_text(json.dumps(manifest), encoding="utf-8")

    backfill.curate_picker(tmp_path, 2, "2.3.5")

    updated = json.loads((language / "versions.json").read_text(encoding="utf-8"))
    assert [entry["listed"] for entry in updated["versions"]] == [
        False,
        True,
        True,
    ]
    assert (language / "versions.html").is_file()
