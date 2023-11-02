"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplater,
    TemplatedFile,
)
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFileSlice,
    iter_indices_of_newlines,
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


SIMPLE_FILE_KWARGS = {
    "fname": "test.sql",
    "source_str": "01234\n6789{{foo}}fo\nbarss",
    "templated_str": "01234\n6789x\nfo\nbarss",
    "sliced_file": [
        TemplatedFileSlice(*args)
        for args in [
            ("literal", slice(0, 10, None), slice(0, 10, None)),
            ("templated", slice(10, 17, None), slice(10, 12, None)),
            ("literal", slice(17, 25, None), slice(12, 20, None)),
        ]
    ],
    "raw_sliced": [
        RawFileSlice(*args)
        for args in [
            ("x" * 10, "literal", 0),
            ("x" * 7, "templated", 10),
            ("x" * 8, "literal", 17),
        ]
    ],
}

COMPLEX_FILE_KWARGS = {
    "fname": "test.sql",
    "sliced_file": [
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
    ],
    "raw_sliced": [
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
    ],
}
COMPLEX_FILE_KWARGS["source_str"] = "".join(
    s.raw for s in COMPLEX_FILE_KWARGS["raw_sliced"]
)


@pytest.mark.parametrize(
    "tf_kwargs,in_charpos,out_line_no,out_line_pos",
    [
        # Simple examples
        (
            SIMPLE_FILE_KWARGS,
            0,
            1,
            1,
        ),
        (
            SIMPLE_FILE_KWARGS,
            20,
            3,
            1,
        ),
        (
            SIMPLE_FILE_KWARGS,
            24,
            3,
            5,
        ),
    ],
)
def test__templated_file_get_line_pos_of_char_pos(
    tf_kwargs,
    in_charpos,
    out_line_no,
    out_line_pos,
):
    """Test TemplatedFile.get_line_pos_of_char_pos."""
    file = TemplatedFile(**tf_kwargs)
    res_line_no, res_line_pos = file.get_line_pos_of_char_pos(in_charpos)
    assert res_line_no == out_line_no
    assert res_line_pos == out_line_pos


@pytest.mark.parametrize(
    "templated_position,inclusive,tf_kwargs,sliced_idx_start,sliced_idx_stop",
    [
        (100, True, COMPLEX_FILE_KWARGS, 10, 11),
        (13, True, COMPLEX_FILE_KWARGS, 0, 3),
        (28, True, COMPLEX_FILE_KWARGS, 2, 5),
        # Check end slicing.
        (12, True, SIMPLE_FILE_KWARGS, 1, 3),
        (20, True, SIMPLE_FILE_KWARGS, 2, 3),
        # Check inclusivity
        (13, False, COMPLEX_FILE_KWARGS, 0, 1),
    ],
)
def test__templated_file_find_slice_indices_of_templated_pos(
    templated_position,
    inclusive,
    tf_kwargs,
    sliced_idx_start,
    sliced_idx_stop,
):
    """Test TemplatedFile._find_slice_indices_of_templated_pos."""
    file = TemplatedFile(**tf_kwargs)
    res_start, res_stop = file._find_slice_indices_of_templated_pos(
        templated_position, inclusive=inclusive
    )
    assert res_start == sliced_idx_start
    assert res_stop == sliced_idx_stop


@pytest.mark.parametrize(
    "in_slice,out_slice,is_literal,tf_kwargs",
    [
        # Simple example
        (
            slice(5, 10),
            slice(5, 10),
            True,
            {
                "sliced_file": [
                    TemplatedFileSlice(
                        "literal", slice(0, 20, None), slice(0, 20, None)
                    )
                ],
                "raw_sliced": [RawFileSlice("x" * 20, "literal", 0)],
                "source_str": "x" * 20,
                "fname": "foo.sql",
            },
        ),
        # Trimming the end of a literal (with things that follow).
        (
            slice(10, 13),
            slice(10, 13),
            True,
            COMPLEX_FILE_KWARGS,
        ),
        # Unrealistic, but should still work
        (
            slice(5, 10),
            slice(55, 60),
            True,
            {
                "sliced_file": [
                    TemplatedFileSlice(
                        "literal", slice(50, 70, None), slice(0, 20, None)
                    )
                ],
                "raw_sliced": [
                    RawFileSlice("x" * 50, "literal", 0),
                    RawFileSlice("x" * 20, "literal", 50),
                ],
                "source_str": "x" * 70,
                "fname": "foo.sql",
            },
        ),
        # Spanning a template
        (
            slice(5, 15),
            slice(5, 20),
            False,
            SIMPLE_FILE_KWARGS,
        ),
        # Handling templated
        (
            slice(5, 15),
            slice(0, 25),
            False,
            # NB: Same as SIMPLE_SLICED_FILE, but with different slice types.
            {
                **SIMPLE_FILE_KWARGS,
                "sliced_file": [
                    TemplatedFileSlice(
                        "templated", slc.source_slice, slc.templated_slice
                    )
                    for slc in SIMPLE_FILE_KWARGS["sliced_file"]
                ],
                "raw_sliced": [
                    RawFileSlice(slc.raw, "templated", slc.source_idx)
                    for slc in SIMPLE_FILE_KWARGS["raw_sliced"]
                ],
            },
        ),
        # Handling single length slices
        (
            slice(10, 10),
            slice(10, 10),
            True,
            SIMPLE_FILE_KWARGS,
        ),
        (
            slice(12, 12),
            slice(17, 17),
            True,
            SIMPLE_FILE_KWARGS,
        ),
        # Dealing with single length elements
        (
            slice(20, 20),
            slice(25, 25),
            True,
            {
                "sliced_file": SIMPLE_FILE_KWARGS["sliced_file"]
                + [
                    TemplatedFileSlice(
                        "comment", slice(25, 35, None), slice(20, 20, None)
                    )
                ],
                "raw_sliced": SIMPLE_FILE_KWARGS["raw_sliced"]
                + [RawFileSlice("x" * 10, "comment", 25)],
                "source_str": SIMPLE_FILE_KWARGS["source_str"] + "x" * 10,
                "fname": "foo.sql",
            },
        ),
        # Just more test coverage
        (
            slice(43, 43),
            slice(87, 87),
            True,
            COMPLEX_FILE_KWARGS,
        ),
        (
            slice(13, 13),
            slice(13, 13),
            True,
            COMPLEX_FILE_KWARGS,
        ),
        (
            slice(186, 186),
            slice(155, 155),
            True,
            COMPLEX_FILE_KWARGS,
        ),
        # Backward slicing.
        (
            slice(100, 130),
            # NB This actually would reference the wrong way around if we
            # just take the points. Here we should handle it gracefully.
            slice(68, 110),
            False,
            COMPLEX_FILE_KWARGS,
        ),
    ],
)
def test__templated_file_templated_slice_to_source_slice(
    in_slice, out_slice, is_literal, tf_kwargs
):
    """Test TemplatedFile.templated_slice_to_source_slice."""
    file = TemplatedFile(**tf_kwargs)
    source_slice = file.templated_slice_to_source_slice(in_slice)
    literal_test = file.is_source_slice_literal(source_slice)
    assert (is_literal, source_slice) == (literal_test, out_slice)


@pytest.mark.parametrize(
    "file,expected_result",
    [
        # Comment example
        (
            TemplatedFile(
                source_str=("a" * 10) + "{# b #}" + ("a" * 10),
                fname="test",
                sliced_file=[
                    TemplatedFileSlice("literal", slice(0, 10), slice(0, 10)),
                    TemplatedFileSlice("templated", slice(10, 17), slice(10, 10)),
                    TemplatedFileSlice("literal", slice(17, 27), slice(10, 20)),
                ],
                raw_sliced=[
                    RawFileSlice("a" * 10, "literal", 0),
                    RawFileSlice("{# b #}", "comment", 10),
                    RawFileSlice("a" * 10, "literal", 17),
                ],
            ),
            [RawFileSlice("{# b #}", "comment", 10)],
        ),
        # Template tags aren't source only.
        (
            TemplatedFile(
                source_str=r"aaa{{ b }}aaa",
                fname="test",
                sliced_file=[
                    TemplatedFileSlice("literal", slice(0, 3), slice(0, 3)),
                    TemplatedFileSlice("templated", slice(3, 10), slice(3, 6)),
                    TemplatedFileSlice("literal", slice(10, 13), slice(6, 9)),
                ],
                raw_sliced=[
                    RawFileSlice("aaa", "literal", 0),
                    RawFileSlice("{{ b }}", "templated", 3),
                    RawFileSlice("aaa", "literal", 10),
                ],
            ),
            [],
        ),
    ],
)
def test__templated_file_source_only_slices(file, expected_result):
    """Test TemplatedFile.source_only_slices."""
    assert file.source_only_slices() == expected_result
