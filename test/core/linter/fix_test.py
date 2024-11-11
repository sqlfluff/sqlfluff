"""Test routines for fixing errors."""

import logging

import pytest

from sqlfluff.core.linter.fix import compute_anchor_edit_info
from sqlfluff.core.linter.patch import FixPatch, generate_source_patches
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    TemplateSegment,
)
from sqlfluff.core.parser.segments.raw import SourceFix
from sqlfluff.core.rules.fix import LintFix
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile
from sqlfluff.core.templaters.base import TemplatedFileSlice


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


templated_file_1 = TemplatedFile.from_string("abc")
templated_file_2 = TemplatedFile(
    "{# blah #}{{ foo }}bc",
    "<testing>",
    "abc",
    [
        TemplatedFileSlice("comment", slice(0, 10), slice(0, 0)),
        TemplatedFileSlice("templated", slice(10, 19), slice(0, 1)),
        TemplatedFileSlice("literal", slice(19, 21), slice(1, 3)),
    ],
    [
        RawFileSlice("{# blah #}", "comment", 0),
        RawFileSlice("{{ foo }}", "templated", 10),
        RawFileSlice("bc", "literal", 19),
    ],
)


@pytest.mark.parametrize(
    "tree,templated_file,expected_result",
    [
        # Trivial example
        (
            RawSegment(
                "abc",
                PositionMarker(slice(0, 3), slice(0, 3), templated_file_1),
                "code",
            ),
            templated_file_1,
            [],
        ),
        # Simple literal edit example
        (
            RawSegment(
                "abz",
                PositionMarker(slice(0, 3), slice(0, 3), templated_file_1),
                "code",
            ),
            templated_file_1,
            [FixPatch(slice(0, 3), "abz", "literal", slice(0, 3), "abc", "abc")],
        ),
        # Nested literal edit example
        (
            BaseSegment(
                (
                    RawSegment(
                        "a",
                        PositionMarker(slice(0, 1), slice(0, 1), templated_file_1),
                        "code",
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(1, 2), slice(1, 2), templated_file_1),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(2, 3), slice(2, 3), templated_file_1),
                        "code",
                    ),
                )
            ),
            templated_file_1,
            [FixPatch(slice(0, 3), "abz", "literal", slice(0, 3), "abc", "abc")],
        ),
        # More complicated templating example
        (
            BaseSegment(
                (
                    TemplateSegment(
                        PositionMarker(slice(0, 10), slice(0, 0), templated_file_2),
                        "{# blah #}",
                        "comment",
                    ),
                    RawSegment(
                        "a",
                        PositionMarker(slice(10, 20), slice(0, 1), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(19, 20), slice(1, 2), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(20, 21), slice(2, 3), templated_file_2),
                        "code",
                    ),
                )
            ),
            templated_file_2,
            [FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c")],
        ),
        # Templating example with fixes
        (
            BaseSegment(
                (
                    TemplateSegment(
                        PositionMarker(slice(0, 10), slice(0, 0), templated_file_2),
                        "{# blah #}",
                        "comment",
                        source_fixes=[
                            SourceFix("{# fixed #}", slice(0, 10), slice(0, 0))
                        ],
                    ),
                    RawSegment(
                        "a",
                        PositionMarker(slice(10, 19), slice(0, 1), templated_file_2),
                        "code",
                        source_fixes=[
                            SourceFix("{{ bar }}", slice(10, 19), slice(0, 1))
                        ],
                    ),
                    RawSegment(
                        "b",
                        PositionMarker(slice(19, 20), slice(1, 2), templated_file_2),
                        "code",
                    ),
                    RawSegment(
                        "z",
                        PositionMarker(slice(20, 21), slice(2, 3), templated_file_2),
                        "code",
                    ),
                )
            ),
            templated_file_2,
            [
                FixPatch(
                    slice(0, 0), "{# fixed #}", "source", slice(0, 10), "", "{# blah #}"
                ),
                FixPatch(
                    slice(0, 1), "{{ bar }}", "source", slice(10, 19), "a", "{{ foo }}"
                ),
                FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c"),
            ],
        ),
    ],
)
def test__fix__generate_source_patches(tree, templated_file, expected_result, caplog):
    """Test generate_source_patches.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = generate_source_patches(tree, templated_file)
    assert result == expected_result
