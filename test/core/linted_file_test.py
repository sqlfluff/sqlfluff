"""The Test file for the linter class."""

import pytest
import logging

from sqlfluff.core.linter.linted_file import LintedFile, LintedVariant
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    FixPatch,
    RawSegment,
    BaseSegment,
    TemplateSegment,
)
from sqlfluff.core.parser.segments.raw import SourceFix
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
        # Trivial example.
        # No edits in a single character file. Slice should be one
        # character long.
        ([], [], "a", [slice(0, 1)]),
        # Simple replacement.
        # We've yielded a patch to change a single character. This means
        # we should get only slices for that character, and for the
        # unchanged file around it.
        (
            [FixPatch(slice(1, 2), "d", "", slice(1, 2), "b", "b")],
            [],
            "abc",
            [slice(0, 1), slice(1, 2), slice(2, 3)],
        ),
        # Templated no fixes.
        # A templated file, but with no fixes, so no subdivision of the
        # file is required and we should just get a single slice.
        (
            [],
            [],
            "a {{ b }} c",
            [slice(0, 11)],
        ),
        # Templated example with a source-only slice.
        # A templated file, but with no fixes, so no subdivision of the
        # file is required and we should just get a single slice. While
        # there is handling for "source only" slices like template
        # comments, in this case no additional slicing is required
        # because no edits have been made.
        (
            [],
            [RawFileSlice("{# b #}", "comment", 2)],
            "a {# b #} c",
            [slice(0, 11)],
        ),
        # Templated fix example with a source-only slice.
        # We're making an edit adjacent to a source only slice. Edits
        # _before_ source only slices currently don't trigger additional
        # slicing. This is fine.
        (
            [FixPatch(slice(0, 1), "a ", "", slice(0, 1), "a", "a")],
            [RawFileSlice("{# b #}", "comment", 1)],
            "a{# b #}c",
            [slice(0, 1), slice(1, 9)],
        ),
        # Templated fix example with a source-only slice.
        # We've made an edit directly _after_ a source only slice
        # which should trigger the logic to ensure that the source
        # only slice isn't included in the source mapping of the
        # edit.
        # TODO: given that the logic is based on the _type_
        # of the slice (e.g. comment), would we handle a
        # template tag which returns an empty string correctly?
        (
            [FixPatch(slice(1, 2), " c", "", slice(8, 9), "c", "c")],
            [RawFileSlice("{# b #}", "comment", 1)],
            "a{# b #}cc",
            [slice(0, 1), slice(1, 8), slice(8, 9), slice(9, 10)],
        ),
        # Templated example with a source-only slice.
        # Here we're making the fix to the templated slice. This
        # checks that we don't duplicate or fumble the slice
        # generation when we're explicitly trying to edit the source.
        # TODO: Should we be using the fix type (e.g. "source")
        # to somehow determine whether the fix is "safe"?
        (
            [FixPatch(slice(2, 2), "{# fixed #}", "", slice(2, 9), "", "")],
            [RawFileSlice("{# b #}", "comment", 2)],
            "a {# b #} c",
            [slice(0, 2), slice(2, 9), slice(9, 11)],
        ),
        # Illustrate potential templating bug (case from L046).
        # In this case we have fixes for all our tempolated sections
        # and they are all close to each other and so may be either
        # skipped or duplicated if the logic is not precise.
        (
            [
                FixPatch(
                    templated_slice=slice(14, 14),
                    fixed_raw="{%+ if true -%}",
                    patch_category="source",
                    source_slice=slice(14, 27),
                    templated_str="",
                    source_str="{%+if true-%}",
                ),
                FixPatch(
                    templated_slice=slice(14, 14),
                    fixed_raw="{{ ref('foo') }}",
                    patch_category="source",
                    source_slice=slice(28, 42),
                    templated_str="",
                    source_str="{{ref('foo')}}",
                ),
                FixPatch(
                    templated_slice=slice(17, 17),
                    fixed_raw="{%- endif %}",
                    patch_category="source",
                    source_slice=slice(43, 53),
                    templated_str="",
                    source_str="{%-endif%}",
                ),
            ],
            [
                RawFileSlice(
                    raw="{%+if true-%}",
                    slice_type="block_start",
                    source_idx=14,
                    block_idx=0,
                ),
                RawFileSlice(
                    raw="{%-endif%}",
                    slice_type="block_end",
                    source_idx=43,
                    block_idx=1,
                ),
            ],
            "SELECT 1 from {%+if true-%} {{ref('foo')}} {%-endif%}",
            [
                slice(0, 14),
                slice(14, 27),
                slice(27, 28),
                slice(28, 42),
                slice(42, 43),
                slice(43, 53),
            ],
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
                ]
            ),
            templated_file_2,
            [FixPatch(slice(2, 3), "z", "literal", slice(20, 21), "c", "c")],
        ),
        # Templating example with fixes
        (
            BaseSegment(
                [
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
                ]
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
def test__linted_variant__generate_source_patches(
    tree, templated_file, expected_result, caplog
):
    """Test _generate_source_patches.

    This is part of fix_string().
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
        result = LintedVariant._generate_source_patches(tree, templated_file)
    assert result == expected_result
