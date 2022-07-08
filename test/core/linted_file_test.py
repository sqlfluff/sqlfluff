"""The Test file for the linter class."""

import pytest
import logging

from sqlfluff.core.linter import LintedFile
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import FixPatch, RawSegment, BaseSegment
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile
from sqlfluff.core.templaters.base import TemplatedFileSlice


@pytest.mark.parametrize(
    "source_slices,source_patches,raw_source_string,expected_result",
    # NOTE: For all of these examples we're not setting the patch_category
    # of the fix patches. They're not used at this step so irrelevant for
    # testing.
    [
        # Trivial example
        ([slice(0, 1)], [], "a", "a"),
        # Simple replacement
        (
            [slice(0, 1), slice(1, 2), slice(2, 3)],
            [FixPatch(slice(1, 2), "d", "", slice(1, 2), "b", "b")],
            "abc",
            "adc",
        ),
        # Simple insertion
        (
            [slice(0, 1), slice(1, 1), slice(1, 2)],
            [FixPatch(slice(1, 1), "b", "", slice(1, 1), "", "")],
            "ac",
            "abc",
        ),
        # Simple deletion
        (
            [slice(0, 1), slice(1, 2), slice(2, 3)],
            [FixPatch(slice(1, 2), "", "", slice(1, 2), "b", "b")],
            "abc",
            "ac",
        ),
        # Illustrative templated example (although practically at
        # this step, the routine shouldn't care if it's templated).
        (
            [slice(0, 2), slice(2, 7), slice(7, 9)],
            [FixPatch(slice(2, 3), "{{ b }}", "", slice(2, 7), "b", "{{b}}")],
            "a {{b}} c",
            "a {{ b }} c",
        ),
    ],
)
def test__linted_file__build_up_fixed_source_string(
    source_slices, source_patches, raw_source_string, expected_result, caplog
):
    """Test _build_up_fixed_source_string.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = LintedFile._build_up_fixed_source_string(
            source_slices, source_patches, raw_source_string
        )
    assert result == expected_result


@pytest.mark.parametrize(
    "source_patches,source_only_slices,raw_source_string,expected_result",
    # NOTE: For all of these examples we're not setting the patch_category
    # of the fix patches. They're not used at this step so irrelevant for
    # testing.
    [
        # Trivial example
        ([], [], "a", [slice(0, 1)]),
        # Simple replacement
        (
            [FixPatch(slice(1, 2), "d", "", slice(1, 2), "b", "b")],
            [],
            "abc",
            [slice(0, 1), slice(1, 2), slice(2, 3)],
        ),
        # Basic templated example
        # NOTE: No fixes so just one slice.
        (
            [],
            [],
            "a {{ b }} c",
            [slice(0, 11)],
        ),
        # Templated example with a source-only slice.
        # NOTE: No fixes so just one slice.
        (
            [],
            [RawFileSlice("{# b #}", "comment", 2)],
            "a {# b #} c",
            [slice(0, 11)],
        ),
        # Templated fix example with a source-only slice.
        # NOTE: Correct slicing example
        (
            [FixPatch(slice(0, 1), "a ", "", slice(0, 1), "a", "a")],
            [RawFileSlice("{# b #}", "comment", 1)],
            "a{# b #}c",
            [slice(0, 1), slice(1, 9)],
        ),
        # Templated fix example with a source-only slice.
        # NOTE: We insert a slice for the source only slice.
        # TODO: given that the logic is based on the _type_
        # of the slice (e.g. comment), would we handle a
        # template tag which returns an empty string correctly?
        (
            [FixPatch(slice(1, 2), " c", "", slice(8, 9), "c", "c")],
            [RawFileSlice("{# b #}", "comment", 1)],
            "a{# b #}cc",
            [slice(0, 1), slice(1, 8), slice(8, 9), slice(9, 10)],
        ),
    ],
)
def test__linted_file__slice_source_file_using_patches(
    source_patches, source_only_slices, raw_source_string, expected_result, caplog
):
    """Test _slice_source_file_using_patches.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = LintedFile._slice_source_file_using_patches(
            source_patches, source_only_slices, raw_source_string
        )
    assert result == expected_result


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
                [
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
                ]
            ),
            templated_file_1,
            [FixPatch(slice(0, 3), "abz", "literal", slice(0, 3), "abc", "abc")],
        ),
        # More complicated templating example
        (
            BaseSegment(
                [
                    RawSegment(
                        "a",
                        PositionMarker(slice(0, 20), slice(0, 1), templated_file_2),
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
                ]
            ),
            templated_file_2,
            [FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c")],
        ),
    ],
)
def test__linted_file__generate_source_patches(
    tree, templated_file, expected_result, caplog
):
    """Test _generate_source_patches.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = LintedFile._generate_source_patches(tree, templated_file)
    assert result == expected_result
