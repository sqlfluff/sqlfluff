"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplater,
    TemplatedFile,
)

from sqlfluff.core.templaters.base import (
    iter_indices_of_newlines,
    RawFileSlice,
    TemplatedFileSlice,
)


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


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplater()
    instr = "SELECT * FROM {{blah}}"
    outstr, _ = t.process(in_str=instr, fname="test")
    assert instr == str(outstr)


SIMPLE_SOURCE_STR = "01234\n6789{{foo}}fo\nbarss"
SIMPLE_TEMPLATED_STR = "01234\n6789x\nfo\nbarfss"
SIMPLE_SLICED_FILE = [
    TemplatedFileSlice(*args)
    for args in [
        ("literal", slice(0, 10, None), slice(0, 10, None)),
        ("templated", slice(10, 17, None), slice(10, 12, None)),
        ("literal", slice(17, 25, None), slice(12, 20, None)),
    ]
]
SIMPLE_RAW_SLICED_FILE = [
    RawFileSlice(*args)
    for args in [
        ("x" * 10, "literal", 0),
        ("x" * 7, "templated", 10),
        ("x" * 8, "literal", 17),
    ]
]

COMPLEX_SLICED_FILE = [
    TemplatedFileSlice(*args)
    for args in [
        ("literal", slice(0, 13, None), slice(0, 13, None)),
        ("comment", slice(13, 29, None), slice(13, 13, None)),
        ("literal", slice(29, 44, None), slice(13, 28, None)),
        ("block_start", slice(44, 68, None), slice(28, 28, None)),
        ("literal", slice(68, 81, None), slice(28, 41, None)),
        ("templated", slice(81, 86, None), slice(41, 42, None)),
        ("literal", slice(86, 110, None), slice(42, 66, None)),
        ("templated", slice(68, 86, None), slice(66, 76, None)),
        ("literal", slice(68, 81, None), slice(76, 89, None)),
        ("templated", slice(81, 86, None), slice(89, 90, None)),
        ("literal", slice(86, 110, None), slice(90, 114, None)),  #
        ("templated", slice(68, 86, None), slice(114, 125, None)),
        ("literal", slice(68, 81, None), slice(125, 138, None)),  #
        ("templated", slice(81, 86, None), slice(138, 139, None)),
        ("literal", slice(86, 110, None), slice(139, 163, None)),
        ("templated", slice(110, 123, None), slice(163, 166, None)),
        ("literal", slice(123, 132, None), slice(166, 175, None)),
        ("block_end", slice(132, 144, None), slice(175, 175, None)),
        ("literal", slice(144, 155, None), slice(175, 186, None)),
        ("block_start", slice(155, 179, None), slice(186, 186, None)),
        ("literal", slice(179, 189, None), slice(186, 196, None)),
        ("templated", slice(189, 194, None), slice(196, 197, None)),
        ("literal", slice(194, 203, None), slice(197, 206, None)),
        ("literal", slice(179, 189, None), slice(206, 216, None)),
        ("templated", slice(189, 194, None), slice(216, 217, None)),
        ("literal", slice(194, 203, None), slice(217, 226, None)),
        ("literal", slice(179, 189, None), slice(226, 236, None)),
        ("templated", slice(189, 194, None), slice(236, 237, None)),
        ("literal", slice(194, 203, None), slice(237, 246, None)),
        ("block_end", slice(203, 215, None), slice(246, 246, None)),
        ("literal", slice(215, 230, None), slice(246, 261, None)),
    ]
]
COMPLEX_RAW_SLICED_FILE = [
    RawFileSlice(*args)
    for args in [
        # All contain dummy strings for now.
        ("x" * 13, "literal", 0),
        ("x" * 16, "comment", 13),
        ("x" * 15, "literal", 29),
        ("x" * 24, "block_start", 44),
        ("x" * 13, "literal", 68),
        ("x" * 5, "templated", 81),
        ("x" * 24, "literal", 86),
        ("x" * 13, "templated", 110),
        ("x" * 9, "literal", 123),
        ("x" * 12, "block_end", 132),
        ("x" * 11, "literal", 144),
        ("x" * 24, "block_start", 155),
        ("x" * 10, "literal", 179),
        ("x" * 5, "templated", 189),
        ("x" * 9, "literal", 194),
        ("x" * 12, "block_end", 203),
        ("x" * 15, "literal", 215),
    ]
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
    """Test TemplatedFile.get_line_pos_of_char_pos."""
    file = TemplatedFile(
        source_str=source_str,
        templated_str=templated_str,
        sliced_file=file_slices,
        fname="test",
        check_consistency=False,
    )
    res_line_no, res_line_pos = file.get_line_pos_of_char_pos(in_charpos)
    assert res_line_no == out_line_no
    assert res_line_pos == out_line_pos


@pytest.mark.parametrize(
    "templated_position,inclusive,file_slices,sliced_idx_start,sliced_idx_stop",
    [
        (100, True, COMPLEX_SLICED_FILE, 10, 11),
        (13, True, COMPLEX_SLICED_FILE, 0, 3),
        (28, True, COMPLEX_SLICED_FILE, 2, 5),
        # Check end slicing.
        (12, True, SIMPLE_SLICED_FILE, 1, 3),
        (20, True, SIMPLE_SLICED_FILE, 2, 3),
        # Check inclusivity
        (13, False, COMPLEX_SLICED_FILE, 0, 1),
    ],
)
def test__templated_file_find_slice_indices_of_templated_pos(
    templated_position, inclusive, file_slices, sliced_idx_start, sliced_idx_stop
):
    """Test TemplatedFile._find_slice_indices_of_templated_pos."""
    file = TemplatedFile(
        source_str="Dummy String", sliced_file=file_slices, fname="test"
    )
    res_start, res_stop = file._find_slice_indices_of_templated_pos(
        templated_position, inclusive=inclusive
    )
    assert res_start == sliced_idx_start
    assert res_stop == sliced_idx_stop


@pytest.mark.parametrize(
    "in_slice,out_slice,is_literal,file_slices,raw_slices",
    [
        # Simple example
        (
            slice(5, 10),
            slice(5, 10),
            True,
            [TemplatedFileSlice("literal", slice(0, 20, None), slice(0, 20, None))],
            [RawFileSlice("x" * 20, "literal", 0)],
        ),
        # Trimming the end of a literal (with things that follow).
        (
            slice(10, 13),
            slice(10, 13),
            True,
            COMPLEX_SLICED_FILE,
            COMPLEX_RAW_SLICED_FILE,
        ),
        # Unrealistic, but should still work
        (
            slice(5, 10),
            slice(55, 60),
            True,
            [TemplatedFileSlice("literal", slice(50, 70, None), slice(0, 20, None))],
            [RawFileSlice("x" * 50, "literal", 0), ("x" * 20, "literal", 50)],
        ),
        # Spanning a template
        (
            slice(5, 15),
            slice(5, 20),
            False,
            SIMPLE_SLICED_FILE,
            SIMPLE_RAW_SLICED_FILE,
        ),
        # Handling templated
        (
            slice(5, 15),
            slice(0, 25),
            False,
            # NB: Same as SIMPLE_SLICED_FILE, but with different slice types.
            [
                TemplatedFileSlice("templated", slc.source_slice, slc.templated_slice)
                for slc in SIMPLE_SLICED_FILE
            ],
            [
                RawFileSlice(slc.raw, "templated", slc.source_idx)
                for slc in SIMPLE_RAW_SLICED_FILE
            ],
        ),
        # Handling single length slices
        (
            slice(10, 10),
            slice(10, 10),
            True,
            SIMPLE_SLICED_FILE,
            SIMPLE_RAW_SLICED_FILE,
        ),
        (
            slice(12, 12),
            slice(17, 17),
            True,
            SIMPLE_SLICED_FILE,
            SIMPLE_RAW_SLICED_FILE,
        ),
        # Dealing with single length elements
        (
            slice(20, 20),
            slice(25, 25),
            True,
            SIMPLE_SLICED_FILE
            + [TemplatedFileSlice("comment", slice(25, 35, None), slice(20, 20, None))],
            SIMPLE_RAW_SLICED_FILE + [RawFileSlice("x" * 10, "comment", 25)],
        ),
        # Just more test coverage
        (
            slice(43, 43),
            slice(87, 87),
            True,
            COMPLEX_SLICED_FILE,
            COMPLEX_RAW_SLICED_FILE,
        ),
        (
            slice(13, 13),
            slice(13, 13),
            True,
            COMPLEX_SLICED_FILE,
            COMPLEX_RAW_SLICED_FILE,
        ),
        (
            slice(186, 186),
            slice(155, 155),
            True,
            COMPLEX_SLICED_FILE,
            COMPLEX_RAW_SLICED_FILE,
        ),
        # Backward slicing.
        (
            slice(100, 130),
            # NB This actually would reference the wrong way around if we
            # just take the points. Here we should handle it gracefully.
            slice(68, 110),
            False,
            COMPLEX_SLICED_FILE,
            COMPLEX_RAW_SLICED_FILE,
        ),
    ],
)
def test__templated_file_templated_slice_to_source_slice(
    in_slice, out_slice, is_literal, file_slices, raw_slices
):
    """Test TemplatedFile.templated_slice_to_source_slice."""
    file = TemplatedFile(
        source_str="Dummy String",
        sliced_file=file_slices,
        raw_sliced=[
            rs if isinstance(rs, RawFileSlice) else RawFileSlice(*rs)
            for rs in raw_slices
        ],
        fname="test",
        check_consistency=False,
    )
    source_slice = file.templated_slice_to_source_slice(in_slice)
    literal_test = file.is_source_slice_literal(source_slice)
    assert (is_literal, source_slice) == (literal_test, out_slice)


def test__templated_file_source_only_slices():
    """Test TemplatedFile.source_only_slices."""
    file = TemplatedFile(
        source_str=" Dummy String again ",  # NB: has length 20
        fname="test",
        raw_sliced=[
            RawFileSlice("a" * 10, "literal", 0),
            RawFileSlice("b" * 7, "comment", 10),
            RawFileSlice("a" * 10, "literal", 17),
        ],
        check_consistency=False,
    )
    assert file.source_only_slices() == [RawFileSlice("b" * 7, "comment", 10)]
