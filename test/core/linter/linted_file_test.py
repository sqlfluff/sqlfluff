"""Tests covering the LintedFile class and it's methods."""

import logging

import pytest

from sqlfluff.core.linter import LintedFile
from sqlfluff.core.linter.patch import FixPatch
from sqlfluff.core.templaters import RawFileSlice


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
        # Illustrate potential templating bug (case from JJ01).
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


@pytest.mark.parametrize(
    "case",
    [
        dict(
            name="utf8_create",
            fname="test.sql",
            encoding="utf-8",
            existing=None,
            update="def",
            expected="def",
        ),
        dict(
            name="utf8_update",
            fname="test.sql",
            encoding="utf-8",
            existing="abc",
            update="def",
            expected="def",
        ),
        dict(
            name="utf8_special_char",
            fname="test.sql",
            encoding="utf-8",
            existing="abc",
            update="→",  # Special utf-8 character
            expected="→",
        ),
        dict(
            name="incorrect_encoding",
            fname="test.sql",
            encoding="Windows-1252",
            existing="abc",
            update="→",  # Not valid in Windows-1252
            expected="abc",  # File should be unchanged
        ),
    ],
    ids=lambda case: case["name"],
)
def test_safe_create_replace_file(case, tmp_path):
    """Test creating or updating .sql files, various content and encoding."""
    p = tmp_path / case["fname"]
    if case["existing"]:
        p.write_text(case["existing"])
    try:
        LintedFile._safe_create_replace_file(
            str(p), str(p), case["update"], case["encoding"]
        )
    except Exception:
        pass
    actual = p.read_text(encoding=case["encoding"])
    assert case["expected"] == actual
