
"""Fix-loop diagnostics and partial-output regression tests."""

from hashlib import sha256

import pytest

from sqlfluff.core import FluffConfig, Linter


def test_loop_limit_writes_diff_and_returns_partial_output(tmp_path, monkeypatch):
    """One fix pass emits a diff without leaking artifacts into the worktree."""
    monkeypatch.chdir(tmp_path)
    config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01", "runaway_limit": 1})
    config.set_value(["rules", "capitalisation.keywords", "capitalisation_policy"], "upper")
    raw = "select 1;\n"
    linted = Linter(config=config).lint_string(raw, fix=True)
    assert linted.fix_string()[0] == "SELECT 1;\n"
    log = (tmp_path / "sqlfluff_fix_loop_changes.txt").read_text(encoding="utf-8")
    assert "-select 1;" in log
    assert "+SELECT 1;" in log
    assert sha256(raw.encode("utf-8")).hexdigest() in log


def test_loop_limit_diagnostic_io_error_is_visible(tmp_path, monkeypatch):
    """A diagnostic write failure is not reported as a successful fix."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sqlfluff_fix_loop_changes.txt").mkdir()
    config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01", "runaway_limit": 1})
    config.set_value(["rules", "capitalisation.keywords", "capitalisation_policy"], "upper")
    with pytest.raises((PermissionError, IsADirectoryError)):
        Linter(config=config).lint_string("select 1;\n", fix=True)
