"""Tests for the shared picker injector.

Archived pre-cutover versions are Sphinx builds with no picker of their own, and
they are built once and never rebuilt. This is the pass that gives them one.

The script lives outside the package, so it is loaded by path rather than
imported; its filename is not a valid module name.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).parent.parent
INJECT = REPO_ROOT / "docsv" / "scripts" / "inject-shared-picker.py"

# What Read the Docs appends to every served page, reproduced from a live build.
RTD_INJECTION = (
    '<script async="async" src="/_/static/javascript/readthedocs-addons.js">'
    "</script>"
    '<meta name="readthedocs-project-slug" content="sqlfluff">'
    '<meta name="readthedocs-version-slug" content="stable">'
)

PAGE = (
    "<html><head><title>SQLFluff</title>{extra}</head>"
    '<body><div class="sphinxsidebarwrapper"></div></body></html>'
)


def _load_inject() -> ModuleType:
    spec = importlib.util.spec_from_file_location("inject_shared_picker", INJECT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inject() -> ModuleType:
    """Load the injector once for the module."""
    return _load_inject()


def _tree(tmp_path: Path, pages: dict[str, str]) -> Path:
    root = tmp_path / "html"
    root.mkdir()

    for name, content in pages.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return root


def test_picker_assets_are_added_to_every_page(inject, tmp_path):
    """Including pages nested below the version root."""
    root = _tree(
        tmp_path,
        {
            "index.html": PAGE.format(extra=""),
            "configuration/index.html": PAGE.format(extra=""),
        },
    )

    assert inject.inject(root, "/en/shared/") == 2

    for page in ("index.html", "configuration/index.html"):
        content = (root / page).read_text(encoding="utf-8")
        assert '<script src="/en/shared/version-picker.js" defer></script>' in content
        assert '"/en/shared/version-picker.css"' in content


def test_the_read_the_docs_injection_is_stripped(inject, tmp_path):
    """A mirrored page must stop advertising the site being replaced.

    This is also what keeps mirroring available as a fallback for a version that
    no longer builds: the RTD markup is the only RTD-specific thing on the page.
    """
    root = _tree(tmp_path, {"index.html": PAGE.format(extra=RTD_INJECTION)})

    inject.inject(root, "/en/shared/")
    content = (root / "index.html").read_text(encoding="utf-8")

    assert "readthedocs" not in content
    assert "version-picker.js" in content


def test_the_read_the_docs_injection_can_be_kept(inject, tmp_path):
    """The escape hatch, for comparing a mirrored page against the original."""
    root = _tree(tmp_path, {"index.html": PAGE.format(extra=RTD_INJECTION)})

    inject.inject(root, "/en/shared/", strip_rtd=False)

    assert "readthedocs-addons" in (root / "index.html").read_text(encoding="utf-8")


def test_injection_is_idempotent(inject, tmp_path):
    """A tree can be re-injected without accumulating tags.

    Which matters because a version may be assembled more than once — a rebuild
    of an archived version runs the same steps as its first publish.
    """
    root = _tree(tmp_path, {"index.html": PAGE.format(extra="")})

    inject.inject(root, "/en/shared/")
    assert inject.inject(root, "/en/shared/") == 0

    content = (root / "index.html").read_text(encoding="utf-8")

    assert content.count("version-picker.js") == 1


def test_pages_without_a_head_are_left_alone(inject, tmp_path):
    """Not every `.html` file in a Sphinx build is a page."""
    root = _tree(tmp_path, {"fragment.html": "<div>a search result template</div>"})

    assert inject.inject(root, "/en/shared/") == 0
    assert (root / "fragment.html").read_text(encoding="utf-8") == (
        "<div>a search result template</div>"
    )


def test_an_uppercase_head_tag_is_matched(inject, tmp_path):
    """Historical builds are not all lowercase, and none will be rebuilt."""
    root = _tree(tmp_path, {"index.html": "<HTML><HEAD><TITLE>x</TITLE></HEAD></HTML>"})

    assert inject.inject(root, "/en/shared/") == 1
    assert "version-picker.js" in (root / "index.html").read_text(encoding="utf-8")


def test_a_missing_directory_is_an_error(inject, tmp_path):
    """A typo in a backfill run should stop it, not silently archive nothing."""
    with pytest.raises(FileNotFoundError):
        inject.inject(tmp_path / "absent", "/en/shared/")


def test_a_shared_base_without_a_trailing_slash_still_works(inject, tmp_path):
    """Otherwise the URLs concatenate and the picker silently never loads."""
    root = _tree(tmp_path, {"index.html": PAGE.format(extra="")})

    inject.inject(root, "/en/shared")
    content = (root / "index.html").read_text(encoding="utf-8")

    assert '"/en/shared/version-picker.css"' in content
    assert "sharedversion-picker" not in content


def test_a_page_mentioning_the_asset_is_still_injected(inject, tmp_path):
    """The idempotency check must match the tag, not the filename in prose.

    This file is documented in `docsv/README.md`, and the docs document
    themselves, so a page naming the asset is a realistic thing to build.
    """
    root = _tree(
        tmp_path,
        {
            "index.html": PAGE.format(extra="").replace(
                "<body>", "<body><p>loads version-picker.js from /en/shared/</p>"
            )
        },
    )

    assert inject.inject(root, "/en/shared/") == 1
    assert '<script src="/en/shared/version-picker.js"' in (
        root / "index.html"
    ).read_text(encoding="utf-8")
