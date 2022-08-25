"""Tests for templaters."""

import pytest
import logging
from sqlfluff.core.errors import SQLFluffSkipFile

from sqlfluff.core.templaters import PythonTemplater
from sqlfluff.core import SQLTemplaterError, FluffConfig

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice
from sqlfluff.core.templaters.python import IntermediateFileSlice


PYTHON_STRING = "SELECT * FROM {blah}"


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplater(override_context=dict(blah="foo"))
    instr = PYTHON_STRING
    outstr, _ = t.process(in_str=instr, fname="test")
    assert str(outstr) == "SELECT * FROM foo"


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplater(override_context=dict(noblah="foo"))
    instr = PYTHON_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(in_str=instr, fname="test")


@pytest.mark.parametrize(
    "int_slice,templated_str,head_test,tail_test,int_test",
    [
        # Test Invariante
        (
            IntermediateFileSlice(
                "compound",
                slice(0, 5),
                slice(0, 5),
                [RawFileSlice("{{i}}", "templated", 0)],
            ),
            "foo",
            [],
            [],
            IntermediateFileSlice(
                "compound",
                slice(0, 5),
                slice(0, 5),
                [RawFileSlice("{{i}}", "templated", 0)],
            ),
        ),
        # Test Complete Trimming
        (
            IntermediateFileSlice(
                "compound",
                slice(0, 3),
                slice(0, 3),
                [RawFileSlice("foo", "literal", 0)],
            ),
            "foo",
            [TemplatedFileSlice("literal", slice(0, 3), slice(0, 3))],
            [],
            IntermediateFileSlice(
                "compound",
                slice(3, 3),
                slice(3, 3),
                [],
            ),
        ),
        # Test Basic Trimming.
        (
            IntermediateFileSlice(
                "compound",
                slice(0, 11),
                slice(0, 7),
                [
                    RawFileSlice("foo", "literal", 0),
                    RawFileSlice("{{i}}", "templated", 3),
                    RawFileSlice("bar", "literal", 8),
                ],
            ),
            "foo1bar",
            [TemplatedFileSlice("literal", slice(0, 3), slice(0, 3))],
            [TemplatedFileSlice("literal", slice(8, 11), slice(4, 7))],
            IntermediateFileSlice(
                "compound",
                slice(3, 8),
                slice(3, 4),
                [RawFileSlice("{{i}}", "templated", 3)],
            ),
        ),
        # Test stopping at blocks.
        (
            IntermediateFileSlice(
                "compound",
                slice(0, 34),
                slice(0, 24),
                [
                    RawFileSlice("foo", "literal", 0),
                    RawFileSlice("{{for}}", "block_start", 3),
                    RawFileSlice("foo", "literal", 10),
                    RawFileSlice("{{i}}", "literal", 13),
                    RawFileSlice("bar", "literal", 18),
                    RawFileSlice("{{endfor}}", "block_end", 21),
                    RawFileSlice("bar", "literal", 31),
                ],
            ),
            "foofoofoobarfoofoobarbar",
            [
                TemplatedFileSlice("literal", slice(0, 3), slice(0, 3)),
                TemplatedFileSlice("block_start", slice(3, 10), slice(3, 3)),
            ],
            [
                TemplatedFileSlice("block_end", slice(21, 31), slice(21, 21)),
                TemplatedFileSlice("literal", slice(31, 34), slice(21, 24)),
            ],
            IntermediateFileSlice(
                "compound",
                slice(10, 21),
                slice(3, 21),
                [
                    RawFileSlice("foo", "literal", 10),
                    RawFileSlice("{{i}}", "literal", 13),
                    RawFileSlice("bar", "literal", 18),
                ],
            ),
        ),
    ],
)
def test__templater_python_intermediate__trim(
    int_slice, templated_str, head_test, tail_test, int_test
):
    """Test trimming IntermediateFileSlice."""
    h, i, t = int_slice.trim_ends(templated_str=templated_str)
    assert h == head_test
    assert t == tail_test
    assert i == int_test


@pytest.mark.parametrize(
    "mainstr,substrings,positions",
    [
        ("", [], []),
        ("a", ["a"], [[0]]),
        ("foobar", ["o", "b"], [[1, 2], [3]]),
        ("bar foo bar foo", ["bar", "foo"], [[0, 8], [4, 12]]),
    ],
)
def test__templater_python_substring_occurrences(mainstr, substrings, positions):
    """Test _substring_occurrences."""
    occurrences = PythonTemplater._substring_occurrences(mainstr, substrings)
    assert isinstance(occurrences, dict)
    pos_test = [occurrences[substring] for substring in substrings]
    assert pos_test == positions


@pytest.mark.parametrize(
    "test,result",
    [
        ({}, []),
        ({"A": [1]}, [("A", 1)]),
        (
            {"A": [3, 2, 1], "B": [4, 2]},
            [("A", 1), ("A", 2), ("B", 2), ("A", 3), ("B", 4)],
        ),
    ],
)
def test__templater_python_sorted_occurrence_tuples(test, result):
    """Test _sorted_occurrence_tuples."""
    assert PythonTemplater._sorted_occurrence_tuples(test) == result


@pytest.mark.parametrize(
    "test,result",
    [
        ("", []),
        ("foo", [RawFileSlice("foo", "literal", 0)]),
        (
            "foo {bar} z {{ y",
            [
                RawFileSlice("foo ", "literal", 0),
                RawFileSlice("{bar}", "templated", 4),
                RawFileSlice(" z ", "literal", 9),
                RawFileSlice("{{", "escaped", 12),
                RawFileSlice(" y", "literal", 14),
            ],
        ),
    ],
)
def test__templater_python_slice_template(test, result):
    """Test _slice_template."""
    resp = list(PythonTemplater._slice_template(test))
    # check contigious
    assert "".join(elem.raw for elem in resp) == test
    # check indices
    idx = 0
    for raw_file_slice in resp:
        assert raw_file_slice.source_idx == idx
        idx += len(raw_file_slice.raw)
    # Check total result
    assert resp == result


@pytest.mark.parametrize(
    "raw_sliced,literals,raw_occurrences,templated_occurrences,templated_length,result",
    [
        ([], [], {}, {}, 0, []),
        (
            [RawFileSlice("foo", "literal", 0)],
            ["foo"],
            {"foo": [0]},
            {"foo": [0]},
            3,
            [
                IntermediateFileSlice(
                    "invariant",
                    slice(0, 3, None),
                    slice(0, 3, None),
                    [RawFileSlice("foo", "literal", 0)],
                )
            ],
        ),
    ],
)
def test__templater_python_split_invariants(
    raw_sliced,
    literals,
    raw_occurrences,
    templated_occurrences,
    templated_length,
    result,
):
    """Test _split_invariants."""
    resp = list(
        PythonTemplater._split_invariants(
            raw_sliced,
            literals,
            raw_occurrences,
            templated_occurrences,
            templated_length,
        )
    )
    # check result
    assert resp == result


@pytest.mark.parametrize(
    "split_file,raw_occurrences,templated_occurrences,templated_str,result",
    [
        ([], {}, {}, "", []),
        (
            [
                IntermediateFileSlice(
                    "invariant",
                    slice(0, 3, None),
                    slice(0, 3, None),
                    [RawFileSlice("foo", "literal", 0)],
                )
            ],
            {"foo": [0]},
            {"foo": [0]},
            "foo",
            [TemplatedFileSlice("literal", slice(0, 3, None), slice(0, 3, None))],
        ),
        (
            [
                IntermediateFileSlice(
                    "invariant",
                    slice(0, 7, None),
                    slice(0, 7, None),
                    [RawFileSlice("SELECT ", "literal", 0)],
                ),
                IntermediateFileSlice(
                    "compound",
                    slice(7, 24, None),
                    slice(7, 22, None),
                    [
                        RawFileSlice("{blah}", "templated", 7),
                        RawFileSlice(", ", "literal", 13),
                        RawFileSlice("{foo:.2f}", "templated", 15),
                    ],
                ),
                IntermediateFileSlice(
                    "invariant",
                    slice(24, 33, None),
                    slice(22, 31, None),
                    [RawFileSlice(" as foo, ", "literal", 22)],
                ),
                IntermediateFileSlice(
                    "simple",
                    slice(33, 38, None),
                    slice(31, 35, None),
                    [RawFileSlice("{bar}", "templated", 33)],
                ),
                IntermediateFileSlice(
                    "invariant",
                    slice(38, 41, None),
                    slice(35, 38, None),
                    [RawFileSlice(", '", "literal", 35)],
                ),
                IntermediateFileSlice(
                    "compound",
                    slice(41, 45, None),
                    slice(38, 40, None),
                    [
                        RawFileSlice("{{", "escaped", 41),
                        RawFileSlice("}}", "escaped", 43),
                    ],
                ),
                IntermediateFileSlice(
                    "invariant",
                    slice(45, 76, None),
                    slice(40, 71, None),
                    [RawFileSlice("' as convertable from something", "literal", 40)],
                ),
            ],
            {
                "SELECT ": [0],
                ", ": [13, 31, 38],
                " as foo, ": [24],
                ", '": [38],
                "' as convertable from something": [45],
            },
            {
                "SELECT ": [0],
                ", ": [14, 29, 35],
                " as foo, ": [22],
                ", '": [35],
                "' as convertable from something": [40],
            },
            "SELECT nothing, 435.24 as foo, spam, '{}' as convertable from something",
            [
                TemplatedFileSlice("literal", slice(0, 7, None), slice(0, 7, None)),
                TemplatedFileSlice("templated", slice(7, 13, None), slice(7, 14, None)),
                TemplatedFileSlice("literal", slice(13, 15, None), slice(14, 16, None)),
                TemplatedFileSlice(
                    "templated", slice(15, 24, None), slice(16, 22, None)
                ),
                TemplatedFileSlice("literal", slice(24, 33, None), slice(22, 31, None)),
                TemplatedFileSlice(
                    "templated", slice(33, 38, None), slice(31, 35, None)
                ),
                TemplatedFileSlice("literal", slice(38, 41, None), slice(35, 38, None)),
                TemplatedFileSlice("escaped", slice(41, 45, None), slice(38, 40, None)),
                TemplatedFileSlice("literal", slice(45, 76, None), slice(40, 71, None)),
            ],
        ),
        # Check for recursion error in non-exact raw cases.
        (
            [
                IntermediateFileSlice(
                    "compound",
                    slice(0, 13, None),
                    slice(0, 9, None),
                    [
                        RawFileSlice("{foo}", "templated", 0),
                        RawFileSlice(" , ", "literal", 5),
                        RawFileSlice("{bar}", "templated", 8),
                    ],
                ),
            ],
            {",": [6]},
            {",": [4]},
            "foo , bar",
            [
                TemplatedFileSlice("templated", slice(0, 5, None), slice(0, 3, None)),
                # Alternate implementations which group these next three together
                # would also be fine.
                TemplatedFileSlice("literal", slice(5, 6, None), slice(3, 4, None)),
                TemplatedFileSlice("literal", slice(6, 7, None), slice(4, 5, None)),
                TemplatedFileSlice("literal", slice(7, 8, None), slice(5, 6, None)),
                TemplatedFileSlice("templated", slice(8, 13, None), slice(6, 9, None)),
            ],
        ),
    ],
)
def test__templater_python_split_uniques_coalesce_rest(
    split_file, raw_occurrences, templated_occurrences, templated_str, result, caplog
):
    """Test _split_uniques_coalesce_rest."""
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        resp = list(
            PythonTemplater._split_uniques_coalesce_rest(
                split_file,
                raw_occurrences,
                templated_occurrences,
                templated_str,
            )
        )
    # Check contigious
    prev_slice = None
    for elem in result:
        if prev_slice:
            assert elem[1].start == prev_slice[0].stop
            assert elem[2].start == prev_slice[1].stop
        prev_slice = (elem[1], elem[2])
    # check result
    assert resp == result


@pytest.mark.parametrize(
    "raw_file,templated_file,unwrap_wrapped,result",
    [
        ("", "", True, []),
        (
            "foo",
            "foo",
            True,
            [("literal", slice(0, 3, None), slice(0, 3, None))],
        ),
        (
            "SELECT {blah}, {foo:.2f} as foo, {bar}, '{{}}' as convertable from "
            "something",
            "SELECT nothing, 435.24 as foo, spam, '{}' as convertable from something",
            True,
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("templated", slice(7, 13, None), slice(7, 14, None)),
                ("literal", slice(13, 15, None), slice(14, 16, None)),
                ("templated", slice(15, 24, None), slice(16, 22, None)),
                ("literal", slice(24, 33, None), slice(22, 31, None)),
                ("templated", slice(33, 38, None), slice(31, 35, None)),
                ("literal", slice(38, 41, None), slice(35, 38, None)),
                ("escaped", slice(41, 45, None), slice(38, 40, None)),
                ("literal", slice(45, 76, None), slice(40, 71, None)),
            ],
        ),
        # Test a wrapped example. Given the default config is to unwrap any wrapped
        # queries, it should ignore the ends in the sliced file.
        (
            "SELECT {blah} FROM something",
            "WITH wrap AS (SELECT nothing FROM something) SELECT * FROM wrap",
            True,
            # The sliced version should have trimmed the ends
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("templated", slice(7, 13, None), slice(7, 14, None)),
                ("literal", slice(13, 28, None), slice(14, 29, None)),
            ],
        ),
        (
            "SELECT {blah} FROM something",
            "WITH wrap AS (SELECT nothing FROM something) SELECT * FROM wrap",
            False,  # Test NOT unwrapping it.
            # The sliced version should NOT have trimmed the ends
            [
                ("templated", slice(0, 0, None), slice(0, 14, None)),
                ("literal", slice(0, 7, None), slice(14, 21, None)),
                ("templated", slice(7, 13, None), slice(21, 28, None)),
                ("literal", slice(13, 28, None), slice(28, 43, None)),
                ("templated", slice(28, 28, None), slice(43, 63, None)),
            ],
        ),
    ],
)
def test__templater_python_slice_file(raw_file, templated_file, unwrap_wrapped, result):
    """Test slice_file."""
    _, resp, _ = PythonTemplater().slice_file(
        raw_file,
        templated_file,
        config=FluffConfig(
            configs={"templater": {"unwrap_wrapped_queries": unwrap_wrapped}},
            overrides={"dialect": "ansi"},
        ),
    )
    # Check contigious
    prev_slice = None
    for templated_slice in resp:
        if prev_slice:
            assert templated_slice.source_slice.start == prev_slice[0].stop
            assert templated_slice.templated_slice.start == prev_slice[1].stop
        prev_slice = (templated_slice.source_slice, templated_slice.templated_slice)
    # check result
    assert resp == result


def test__templater_python_large_file_check():
    """Test large file skipping.

    The check is seperately called on each .process() method
    so it makes sense to test a few templaters.
    """
    # First check we can process the file normally without config.
    PythonTemplater().process(in_str="SELECT 1", fname="<string>")
    # Then check we raise a skip exception when config is set low.
    with pytest.raises(SQLFluffSkipFile) as excinfo:
        PythonTemplater().process(
            in_str="SELECT 1",
            fname="<string>",
            config=FluffConfig(
                overrides={"dialect": "ansi", "large_file_skip_char_limit": 2},
            ),
        )

    assert "Length of file" in str(excinfo.value)
