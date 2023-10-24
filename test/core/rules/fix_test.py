"""Test routines for fixing errors."""
import pytest

from sqlfluff.core.rules.fix import LintFix, compute_anchor_edit_info


@pytest.fixture(scope="module")
def raw_segments(generate_test_segments):
    """Construct a list of raw segments as a fixture."""
    return generate_test_segments(["foobar", ".barfoo"])


def test__rules_base_segments_compute_anchor_edit_info(raw_segments):
    """Test BaseSegment.compute_anchor_edit_info()."""
    # Construct a fix buffer, intentionally with:
    # - one duplicate.
    # - two different incompatible fixes on the same segment.
    fixes = [
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="b")]),
    ]
    anchor_info_dict = compute_anchor_edit_info(fixes)
    # Check the target segment is the only key we have.
    assert list(anchor_info_dict.keys()) == [raw_segments[0].uuid]
    anchor_info = anchor_info_dict[raw_segments[0].uuid]
    # Check that the duplicate as been deduplicated.
    # i.e. this isn't 3.
    assert anchor_info.replace == 2
    # Check the fixes themselves.
    # NOTE: There's no duplicated first fix.
    assert anchor_info.fixes == [
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="a")]),
        LintFix.replace(raw_segments[0], [raw_segments[0].edit(raw="b")]),
    ]
    # Check the first replace
    assert anchor_info._first_replace == LintFix.replace(
        raw_segments[0], [raw_segments[0].edit(raw="a")]
    )
