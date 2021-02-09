"""Test fixtures for parser tests."""

import pytest

from sqlfluff.core.dialects import ansi_dialect


@pytest.fixture(scope="function")
def fresh_ansi_dialect():
    """Expand the ansi dialect for use."""
    dialect = ansi_dialect
    dialect.expand()
    return dialect


@pytest.fixture(scope="function")
def seg_list(generate_test_segments):
    """A preset list of segments for testing."""
    return generate_test_segments(["bar", " \t ", "foo", "baar", " \t "])


@pytest.fixture(scope="function")
def bracket_seg_list(generate_test_segments):
    """Another preset list of segments for testing."""
    return generate_test_segments(
        ["bar", " \t ", "(", "foo", "    ", ")", "baar", " \t ", "foo"]
    )
