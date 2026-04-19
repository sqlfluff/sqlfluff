"""Test conditional import paths when pytest is not available."""

import builtins
import sys
from unittest.mock import MagicMock, patch

import pytest


def test_testing_rules_error_message():
    """Test that _ensure_pytest gives helpful error message."""
    from sqlfluff.utils.testing.rules import _ensure_pytest

    import sqlfluff.utils.testing.rules

    original_pytest = sqlfluff.utils.testing.rules.pytest
    try:
        # Temporarily set pytest to None to simulate ImportError path
        sqlfluff.utils.testing.rules.pytest = None
        with pytest.raises(ImportError, match="testutils") as exc_info:
            _ensure_pytest()
        assert "pytest is required" in str(exc_info.value)
    finally:
        # Restore original pytest
        sqlfluff.utils.testing.rules.pytest = original_pytest


def test_testing_logging_error_message():
    """Test that _ensure_pytest_logging gives helpful error message."""
    from sqlfluff.utils.testing.logging import (
        LogCaptureHandler,
        _ensure_pytest_logging,
        _remove_ansi_escape_sequences,
    )

    import sqlfluff.utils.testing.logging

    try:
        # Simulate ImportError path by setting to None
        sqlfluff.utils.testing.logging.LogCaptureHandler = None
        sqlfluff.utils.testing.logging._remove_ansi_escape_sequences = None
        with pytest.raises(ImportError, match="testutils") as exc_info:
            _ensure_pytest_logging()
        assert "pytest is required" in str(exc_info.value)
    finally:
        # Restore original values
        sqlfluff.utils.testing.logging.LogCaptureHandler = LogCaptureHandler
        sqlfluff.utils.testing.logging._remove_ansi_escape_sequences = (
            _remove_ansi_escape_sequences
        )


def test_sqlfluff_init_registers_assert_rewrite_when_pytest_available():
    """sqlfluff.__init__ calls pytest.register_assert_rewrite when pytest is importable."""
    mock_pytest = MagicMock()
    saved = sys.modules.pop("sqlfluff", None)
    try:
        with patch.dict(sys.modules, {"pytest": mock_pytest}):
            import sqlfluff  # noqa: F401
        mock_pytest.register_assert_rewrite.assert_called_once_with(
            "sqlfluff.utils.testing"
        )
    finally:
        if saved is not None:
            sys.modules["sqlfluff"] = saved
        elif "sqlfluff" in sys.modules:
            del sys.modules["sqlfluff"]


def test_sqlfluff_init_handles_missing_pytest():
    """Importing sqlfluff when pytest is unavailable does not raise an error."""
    real_import = builtins.__import__

    def import_without_pytest(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "pytest":
            raise ImportError("No module named 'pytest'")
        return real_import(name, *args, **kwargs)

    saved = sys.modules.pop("sqlfluff", None)
    try:
        with patch("builtins.__import__", side_effect=import_without_pytest):
            import sqlfluff  # noqa: F401
    finally:
        if saved is not None:
            sys.modules["sqlfluff"] = saved
        elif "sqlfluff" in sys.modules:
            del sys.modules["sqlfluff"]


def test_ensure_pytest_does_not_raise_when_pytest_available():
    """_ensure_pytest() succeeds without raising when pytest is importable."""
    from sqlfluff.utils.testing.rules import _ensure_pytest

    _ensure_pytest()  # Should not raise


def test_ensure_pytest_logging_does_not_raise_when_pytest_available():
    """_ensure_pytest_logging() succeeds without raising when pytest is importable."""
    from sqlfluff.utils.testing.logging import _ensure_pytest_logging

    _ensure_pytest_logging()  # Should not raise
