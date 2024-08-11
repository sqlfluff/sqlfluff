"""Test fixtures for parser tests."""

import pytest

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser.segments import TemplateSegment


@pytest.fixture(scope="function")
def fresh_ansi_dialect():
    """Expand the ansi dialect for use."""
    return dialect_selector("ansi")


@pytest.fixture(scope="function")
def test_segments(generate_test_segments):
    """A preset list of segments for testing.

    Includes a templated segment for completeness.
    """
    main_list = generate_test_segments(["bar", " \t ", "foo", "baar", " \t "])
    ts = TemplateSegment(
        pos_marker=main_list[-1].get_end_point_marker(),
        source_str="{# comment #}",
        block_type="comment",
    )
    return main_list + (ts,)
