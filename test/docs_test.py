"""Tests for the documentation build configuration."""

import ast
import sys
from pathlib import Path

# tomllib is only in the stdlib from 3.11+
if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

import sqlfluff

REPO_ROOT = Path(__file__).parent.parent
CONF_PY = REPO_ROOT / "docs" / "source" / "conf.py"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    with open(PYPROJECT, "rb") as config_file:
        return tomllib.load(config_file)


def _eval_conf_stable_version(config: dict) -> object:
    """Evaluate the ``stable_version`` assignment from ``docs/source/conf.py``.

    We evaluate the real expression used by ``conf.py`` (rather than importing
    the module, which has Sphinx side effects and reads generated files) so this
    stays a faithful regression guard for how the docs resolve the version.
    """
    tree = ast.parse(CONF_PY.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "stable_version"
            for target in node.targets
        ):
            expression = ast.Expression(node.value)
            return eval(compile(expression, str(CONF_PY), "eval"), {"config": config})
    raise AssertionError("No `stable_version` assignment found in docs/source/conf.py")


def test_docs_stable_version_matches_package_version():
    """The docs stable version must resolve to the real package version.

    ``docs/source/conf.py`` substitutes ``|release|`` throughout the docs (e.g.
    the ``rev:`` in the pre-commit guide). Previously it read the nested
    ``[tool.sqlfluff_docs] stable_version`` key from ``pyproject.toml`` as a flat
    dotted key, so ``stable_version`` resolved to the literal string
    ``"stable_version"`` instead of the version, rendering an invalid git rev.
    """
    config = _load_pyproject()
    stable_version = _eval_conf_stable_version(config)
    assert stable_version == sqlfluff.__version__
    # Guard against the historical flat-key regression explicitly.
    assert stable_version != "stable_version"
