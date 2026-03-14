"""Tests for use_rust_parser configuration."""

import logging

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER as HAS_RUST_PARSER
except ImportError:
    HAS_RUST_PARSER = False


@pytest.mark.skipif(HAS_RUST_PARSER, reason="Rust parser is available")
def test__linter__use_rust_parser_auto_no_warning(caplog):
    """Test that 'auto' mode doesn't warn when Rust parser is unavailable."""
    config = FluffConfig.from_string("""
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = auto
""")

    with caplog.at_level(logging.WARNING, logger="sqlfluff.linter"):
        lntr = Linter(config=config)
        result = lntr.lint_string("SELECT 1")

        # Should not have any warnings about rust_parser when using 'auto'
        rust_warnings = [
            record for record in caplog.records if "use_rust_parser" in record.message
        ]
        assert len(rust_warnings) == 0, f"Unexpected warnings: {rust_warnings}"
        assert result is not None


@pytest.mark.skipif(HAS_RUST_PARSER, reason="Rust parser is available")
def test__linter__use_rust_parser_true_warns(caplog):
    """Test that explicit True warns when Rust parser is unavailable."""
    # Reset any logging configuration from previous tests
    # (CLI tests may have called setup_logging which sets propagate=False)
    sqlfluff_logger = logging.getLogger("sqlfluff")

    # Store original state
    original_propagate = sqlfluff_logger.propagate
    original_handlers = sqlfluff_logger.handlers[:]

    # Reset to defaults for caplog to work
    sqlfluff_logger.propagate = True
    sqlfluff_logger.handlers.clear()

    try:
        config = FluffConfig.from_string("""
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = True
""")

        with caplog.at_level(logging.WARNING, logger="sqlfluff.linter"):
            lntr = Linter(config=config)
            result = lntr.lint_string("SELECT 1")
            assert result is not None

        # Check after exiting the context manager
        # Should have warning about rust_parser not available
        rust_warnings = [
            record
            for record in caplog.records
            if "use_rust_parser=True but sqlfluffrs not available" in record.message
        ]
        assert len(rust_warnings) == 1, (
            f"Expected 1 warning, got {len(rust_warnings)}:"
            + f" {[r.message for r in caplog.records]}"
        )

        # Check warning message content
        warning_msg = rust_warnings[0].message
        assert "Falling back to Python parser" in warning_msg
        assert "maturin develop" in warning_msg
    finally:
        # Restore original state
        sqlfluff_logger.propagate = original_propagate
        sqlfluff_logger.handlers[:] = original_handlers


def test__linter__use_rust_parser_false_no_rust():
    """Test that False never uses Rust parser."""
    config = FluffConfig.from_string("""
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = False
""")

    lntr = Linter(config=config)
    result = lntr.lint_string("SELECT 1")

    # Should work fine with Python parser
    assert result is not None


def test__linter__use_rust_parser_default_is_auto():
    """Test that default config uses 'auto' mode."""
    config = FluffConfig.from_string("""
[sqlfluff]
dialect = ansi
""")

    use_rust_value = config.get_section(["core", "use_rust_parser"])
    assert use_rust_value == "auto"
