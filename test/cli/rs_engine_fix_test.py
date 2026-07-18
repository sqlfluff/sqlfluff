"""Wiring tests for the experimental Rust-engine façade fix fast path.

Exercises the CLI façade fix routes:

* ``_try_facade_stdin_fix`` — produce native-identical fixes when all selected
  rules are façade-safe and the engine is enabled, and fall back (return
  ``None``) otherwise.
* ``sqlfluff fix`` stdin (``_stdin_fix``) and path (``_paths_fix``) commands —
  the façade fast path echoes/writes fixed output and defers leftovers to the
  native path.

Skipped unless the ``sqlfluffrs`` engine is built.
"""

import pytest

try:
    import sqlfluffrs

    _HAS_ENGINE = hasattr(sqlfluffrs, "engine_parse_to_tree")
except ImportError:  # pragma: no cover
    _HAS_ENGINE = False

import sqlfluff.core.linter.rs_fix as rs_fix
from sqlfluff.cli.commands import _try_facade_stdin_fix, fix
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.utils.testing.cli import invoke_assert_code

pytestmark = pytest.mark.skipif(
    not _HAS_ENGINE, reason="sqlfluffrs.engine_parse_to_tree unavailable"
)


def _linter(
    rules: str, engine: str = "true", dialect: str = "ansi", templater: str = "raw"
) -> Linter:
    return Linter(
        config=FluffConfig(
            overrides={
                "dialect": dialect,
                "rules": rules,
                "use_rust_engine": engine,
                "templater": templater,
            }
        )
    )


def _engine_config(tmp_path) -> str:
    """Write a ``.sqlfluff`` enabling the engine and return its path."""
    cfg = tmp_path / "engine.cfg"
    cfg.write_text("[sqlfluff]\nuse_rust_engine = True\n")
    return str(cfg)


@pytest.mark.parametrize(
    "src,rule,expected",
    [
        ("SeLeCt 1 from b\n", "CP01", "SELECT 1 FROM b\n"),
        ("select 1 from b\n", "CP01", "select 1 from b\n"),  # clean -> unchanged
    ],
)
def test_facade_stdin_fix_fast_path(src: str, rule: str, expected: str) -> None:
    """Fast path fixes correctly (matching the fixture expectation)."""
    assert _try_facade_stdin_fix(_linter(rule), src, None) == expected


def test_facade_stdin_fix_falls_back() -> None:
    """Fall back to the Python path when the façade can't safely cover it."""
    # Non-façade-safe rule (structural fixes).
    assert _try_facade_stdin_fix(_linter("LT01"), "select  1 from b\n", None) is None
    # Engine disabled.
    assert (
        _try_facade_stdin_fix(_linter("CP01", engine="false"), "SeLeCt 1\n", None)
        is None
    )
    # noqa directives are not applied on the façade path.
    assert _try_facade_stdin_fix(_linter("CP01"), "SeLeCt 1 -- noqa\n", None) is None


def test_facade_stdin_fix_unparsable_template_falls_back() -> None:
    """A templater error (engine returns no tree) defers to the Python path."""
    linter = _linter("CP01", templater="jinja")
    # Unclosed Jinja expression -> ``engine_parse_to_tree`` returns ``None``.
    assert _try_facade_stdin_fix(linter, "SELECT {{ 1 \n", None) is None


def test_facade_stdin_fix_remaining_violations_falls_back(monkeypatch) -> None:
    """Defer to Python when violations remain after the façade fix loop."""
    # Pretend the fix loop leaves something behind (non-empty) ...
    monkeypatch.setattr(rs_fix, "facade_violations", lambda *a, **k: [object()])
    assert _try_facade_stdin_fix(_linter("CP01"), "SeLeCt 1 from b\n", None) is None
    # ... and when the re-check itself fails (``None``).
    monkeypatch.setattr(rs_fix, "facade_violations", lambda *a, **k: None)
    assert _try_facade_stdin_fix(_linter("CP01"), "SeLeCt 1 from b\n", None) is None


def test_facade_stdin_fix_exception_falls_back(monkeypatch) -> None:
    """Any exception inside the façade path defers to Python (returns None)."""

    def _boom(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr(rs_fix, "facade_fix_loop", _boom)
    assert _try_facade_stdin_fix(_linter("CP01"), "SeLeCt 1 from b\n", None) is None


def test_facade_cli_stdin_fix(tmp_path) -> None:
    """``sqlfluff fix -`` echoes the façade-fixed output and exits 0."""
    result = invoke_assert_code(
        ret_code=0,
        args=[
            fix,
            [
                "-",
                "--dialect",
                "ansi",
                "--rules",
                "CP01",
                "--config",
                _engine_config(tmp_path),
            ],
        ],
        cli_input="SeLeCt 1 from b\n",
    )
    assert result.stdout == "SELECT 1 FROM b\n"


def test_facade_cli_paths_fix_writes_and_summarises(tmp_path) -> None:
    """The façade fixes a discovered file in place and prints the summary."""
    sql = tmp_path / "a.sql"
    sql.write_text("SeLeCt 1 from b\n")
    result = invoke_assert_code(
        ret_code=0,
        args=[
            fix,
            [
                str(sql),
                "--dialect",
                "ansi",
                "--rules",
                "CP01",
                "--config",
                _engine_config(tmp_path),
            ],
        ],
    )
    assert sql.read_text() == "SELECT 1 FROM b\n"
    assert "fixable linting violations found" in result.stdout


def test_facade_cli_paths_fix_clean_file(tmp_path) -> None:
    """A clean file is façade-handled with no fixables and reports as finished."""
    sql = tmp_path / "clean.sql"
    sql.write_text("SELECT 1 FROM b\n")
    result = invoke_assert_code(
        ret_code=0,
        args=[
            fix,
            [
                str(sql),
                "--dialect",
                "ansi",
                "--rules",
                "CP01",
                "--config",
                _engine_config(tmp_path),
            ],
        ],
    )
    assert sql.read_text() == "SELECT 1 FROM b\n"
    assert "no fixable linting violations found" in result.stdout


def test_facade_cli_paths_fix_defers_remaining(tmp_path) -> None:
    """Files the façade can't handle (noqa) are left for the native path."""
    fixable = tmp_path / "x.sql"
    fixable.write_text("SeLeCt 1 from b\n")
    # ``noqa`` masks aren't applied on the façade path, so this file is handed
    # back to native (facade_remaining is a non-empty list).
    deferred = tmp_path / "y.sql"
    deferred.write_text("SeLeCt 1 from b -- noqa\n")
    invoke_assert_code(
        ret_code=0,
        args=[
            fix,
            [
                str(tmp_path),
                "--dialect",
                "ansi",
                "--rules",
                "CP01",
                "--config",
                _engine_config(tmp_path),
            ],
        ],
    )
    # The façade fixed the plain file; native left the noqa-masked one untouched.
    assert fixable.read_text() == "SELECT 1 FROM b\n"
    assert deferred.read_text() == "SeLeCt 1 from b -- noqa\n"


def test_facade_cli_paths_fix_exception_falls_back(tmp_path, monkeypatch) -> None:
    """If the façade path raises, ``fix`` falls back to the native path."""

    def _boom(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr("sqlfluff.cli.commands._try_facade_paths_fix", _boom)
    sql = tmp_path / "a.sql"
    sql.write_text("SeLeCt 1 from b\n")
    invoke_assert_code(
        ret_code=0,
        args=[
            fix,
            [
                str(sql),
                "--dialect",
                "ansi",
                "--rules",
                "CP01",
                "--config",
                _engine_config(tmp_path),
            ],
        ],
    )
    # Native still applied the fix after the façade path bailed.
    assert sql.read_text() == "SELECT 1 FROM b\n"
