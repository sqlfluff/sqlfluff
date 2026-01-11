"""Test conditional import paths when pytest is not available."""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


def test_testing_rules_error_message():
    """Test that _ensure_pytest gives helpful error message."""
    from sqlfluff.utils.testing.rules import _ensure_pytest, pytest

    # pytest should be available in test environment,
    # so let's test the error path manually
    original_pytest = pytest
    try:
        # Temporarily set pytest to None to simulate ImportError path
        import sqlfluff.utils.testing.rules

        sqlfluff.utils.testing.rules.pytest = None

        try:
            _ensure_pytest()
            assert False, "Should have raised ImportError"
        except ImportError as e:
            assert "testutils" in str(e)
            assert "pytest is required" in str(e)
            print("✓ testing.rules error message test passed")

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

    # Test the error path manually by setting variables to None
    original_handler = LogCaptureHandler
    original_remove_func = _remove_ansi_escape_sequences

    try:
        # Simulate ImportError path by setting to None
        import sqlfluff.utils.testing.logging

        sqlfluff.utils.testing.logging.LogCaptureHandler = None
        sqlfluff.utils.testing.logging._remove_ansi_escape_sequences = None

        try:
            _ensure_pytest_logging()
            assert False, "Should have raised ImportError"
        except ImportError as e:
            assert "testutils" in str(e)
            assert "pytest is required" in str(e)
            print("✓ testing.logging error message test passed")

    finally:
        # Restore original values
        sqlfluff.utils.testing.logging.LogCaptureHandler = original_handler
        sqlfluff.utils.testing.logging._remove_ansi_escape_sequences = (
            original_remove_func
        )


def test_sqlfluff_pytest_assignment():
    """Test that pytest gets assigned correctly in __init__.py."""
    # Read the __init__.py file and verify the conditional import logic exists
    init_path = os.path.join("src", "sqlfluff", "__init__.py")
    with open(init_path, "r") as f:
        content = f.read()

    # Verify the try/except ImportError pattern exists
    assert "try:" in content
    assert "import pytest" in content
    assert "except ImportError:" in content
    assert "pytest = None" in content
    print("✓ sqlfluff.__init__ conditional import structure verified")


def test_testing_rules_import_structure():
    """Test that testing.rules has the correct conditional import structure."""
    rules_path = os.path.join("src", "sqlfluff", "utils", "testing", "rules.py")
    with open(rules_path, "r") as f:
        content = f.read()

    # Verify the try/except ImportError pattern exists
    assert "try:" in content
    assert "import pytest" in content
    assert "except ImportError:" in content
    assert "pytest = None" in content
    assert "def _ensure_pytest():" in content
    print("✓ testing.rules conditional import structure verified")


def test_testing_logging_import_structure():
    """Test that testing.logging has the correct conditional import structure."""
    logging_path = os.path.join("src", "sqlfluff", "utils", "testing", "logging.py")
    with open(logging_path, "r") as f:
        content = f.read()

    # Verify the try/except ImportError pattern exists
    assert "try:" in content
    assert "from _pytest.logging import (" in content
    assert "LogCaptureHandler" in content
    assert "except ImportError:" in content
    assert "LogCaptureHandler = None" in content
    assert "_remove_ansi_escape_sequences = None" in content
    assert "def _ensure_pytest_logging():" in content
    print("✓ testing.logging conditional import structure verified")


if __name__ == "__main__":
    test_sqlfluff_pytest_assignment()
    test_testing_rules_import_structure()
    test_testing_logging_import_structure()
    test_testing_rules_error_message()
    test_testing_logging_error_message()
    print("All conditional import tests passed!")
