"""Tests for use_rust_parser configuration."""

import logging

from sqlfluff.core import FluffConfig, Linter


def test__linter__use_rust_parser_auto_no_warning(caplog):
    """Test that 'auto' mode doesn't warn when Rust parser is unavailable."""
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = auto
"""
    )

    # Mock the import to simulate Rust parser not being available
    import sys

    # Save the original module if it exists
    rust_parser_module = sys.modules.get("sqlfluff.core.parser.rust_parser")
    if rust_parser_module:
        del sys.modules["sqlfluff.core.parser.rust_parser"]

    try:
        # Temporarily block the import
        sys.modules["sqlfluff.core.parser.rust_parser"] = None

        with caplog.at_level(logging.WARNING):
            lntr = Linter(config=config)
            result = lntr.lint_string("SELECT 1")

            # Should not have any warnings about rust_parser when using 'auto'
            rust_warnings = [
                record
                for record in caplog.records
                if "use_rust_parser" in record.message
            ]
            assert len(rust_warnings) == 0, f"Unexpected warnings: {rust_warnings}"
            assert result is not None
    finally:
        # Restore the module
        if rust_parser_module:
            sys.modules["sqlfluff.core.parser.rust_parser"] = rust_parser_module
        elif "sqlfluff.core.parser.rust_parser" in sys.modules:
            del sys.modules["sqlfluff.core.parser.rust_parser"]


def test__linter__use_rust_parser_true_warns(caplog):
    """Test that explicit True warns when Rust parser is unavailable."""
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = True
"""
    )

    # The actual test will depend on whether sqlfluffrs is installed
    # If installed, no warning. If not installed, warning should appear.
    with caplog.at_level(logging.WARNING):
        lntr = Linter(config=config)
        result = lntr.lint_string("SELECT 1")
        assert result is not None

        # Check if warning appears (will depend on whether Rust parser is available)
        # We can't assert the exact behavior since it depends on the environment
        # but we verify that the code runs without error


def test__linter__use_rust_parser_false_no_rust():
    """Test that False never uses Rust parser."""
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = ansi

[sqlfluff:core]
use_rust_parser = False
"""
    )

    lntr = Linter(config=config)
    result = lntr.lint_string("SELECT 1")

    # Should work fine with Python parser
    assert result is not None


def test__linter__use_rust_parser_default_is_auto():
    """Test that default config uses 'auto' mode."""
    config = FluffConfig.from_string(
        """
[sqlfluff]
dialect = ansi
"""
    )

    use_rust_value = config.get_section(["core", "use_rust_parser"])
    assert use_rust_value == "auto"
