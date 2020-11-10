"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplater,
    templater_selector,
    PythonTemplater,
    JinjaTemplater,
    TemplatedFile,
)

from sqlfluff.core.templaters.base import iter_indices_of_newlines


@pytest.mark.parametrize(
    "raw_str,positions",
    [
        ("", []),
        ("foo", []),
        ("foo\nbar", [3]),
        ("\nfoo\n\nbar\nfoo\n\nbar\n", [0, 4, 5, 9, 13, 14, 18]),
    ],
)
def test__indices_of_newlines(raw_str, positions):
    """Test iter_indices_of_newlines."""
    assert list(iter_indices_of_newlines(raw_str)) == positions


def test__templater_selection():
    """Test template selection by name."""
    assert templater_selector().__class__ is JinjaTemplater
    assert templater_selector("raw").__class__ is RawTemplater
    assert templater_selector("python").__class__ is PythonTemplater
    assert templater_selector("jinja").__class__ is JinjaTemplater
    with pytest.raises(ValueError):
        templater_selector("afefhlsakufe")


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplater()
    instr = "SELECT * FROM {{blah}}"
    outstr, _ = t.process(instr)
    assert instr == str(outstr)


SIMPLE_SOURCE_STR = "01234\n6789{{foo}}fo\nbarss"
SIMPLE_TEMPLATED_STR = "01234\n6789x\nfo\nbarfss"
SIMPLE_SLICED_FILE = [
    ("literal", slice(0, 10, None), slice(0, 10, None)),
    ("templated", slice(10, 17, None), slice(10, 12, None)),
    ("literal", slice(17, 25, None), slice(12, 20, None)),
]


@pytest.mark.parametrize(
    "source_str,templated_str,file_slices,in_charpos,out_line_no,out_line_pos",
    [
        # Simple examples
        (SIMPLE_SOURCE_STR, SIMPLE_TEMPLATED_STR, SIMPLE_SLICED_FILE, 0, 1, 1),
        (SIMPLE_SOURCE_STR, SIMPLE_TEMPLATED_STR, SIMPLE_SLICED_FILE, 20, 3, 1),
        (SIMPLE_SOURCE_STR, SIMPLE_TEMPLATED_STR, SIMPLE_SLICED_FILE, 24, 3, 5),
    ],
)
def test__templated_file_get_line_pos_of_char_pos(
    source_str, templated_str, file_slices, in_charpos, out_line_no, out_line_pos
):
    """Test TemplatedFile.template_slice_to_source_slice."""
    file = TemplatedFile(
        source_str=source_str, templated_str=templated_str, sliced_file=file_slices
    )
    res_line_no, res_line_pos = file.get_line_pos_of_char_pos(in_charpos)
    assert res_line_no == out_line_no
    assert res_line_pos == out_line_pos


@pytest.mark.parametrize(
    "in_slice,out_slice,is_literal,file_slices",
    [
        # Simple example
        (
            slice(5, 10),
            slice(5, 10),
            True,
            [("literal", slice(0, 20, None), slice(0, 20, None))],
        ),
        # Unrealistic, but should still work
        (
            slice(5, 10),
            slice(55, 60),
            True,
            [("literal", slice(50, 70, None), slice(0, 20, None))],
        ),
        # Spanning a template
        (
            slice(5, 15),
            slice(5, 20),
            False,
            SIMPLE_SLICED_FILE,
        ),
        # Handling templated
        (
            slice(5, 15),
            slice(0, 25),
            False,
            # NB: Same as SIMPLE_SLICED_FILE, but with different slice types.
            [("templated", elem[1], elem[2]) for elem in SIMPLE_SLICED_FILE],
        ),
        # Handling single length slices
        (
            slice(10, 10),
            slice(10, 10),
            True,
            SIMPLE_SLICED_FILE,
        ),
        (
            slice(12, 12),
            slice(17, 17),
            True,
            SIMPLE_SLICED_FILE,
        ),
    ],
)
def test__templated_file_template_slice_to_source_slice(
    in_slice, out_slice, is_literal, file_slices
):
    """Test TemplatedFile.template_slice_to_source_slice."""
    file = TemplatedFile(source_str="Dummy String", sliced_file=file_slices)
    source_slice, literal_test = file.template_slice_to_source_slice(in_slice)
    assert is_literal == literal_test
    assert source_slice == out_slice


def test__templated_file_untouchable_slices():
    """Test TemplatedFile.template_slice_to_source_slice."""
    file = TemplatedFile(
        source_str=" Dummy String again ",  # NB: has length 20
        sliced_file=[
            ("literal", slice(0, 10, None), slice(0, 10, None)),
            ("literal", slice(17, 27, None), slice(10, 20, None)),
        ],
    )
    assert file.untouchable_slices() == [slice(10, 17)]
