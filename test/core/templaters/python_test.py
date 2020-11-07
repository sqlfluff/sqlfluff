"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import PythonTemplater
from sqlfluff.core import SQLTemplaterError


PYTHON_STRING = "SELECT * FROM {blah}"


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplater(override_context=dict(blah="foo"))
    instr = PYTHON_STRING
    outstr, _ = t.process(instr)
    assert str(outstr) == "SELECT * FROM foo"


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplater(override_context=dict(noblah="foo"))
    instr = PYTHON_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(instr)


@pytest.mark.parametrize(
    "mainstr,substr,positions",
    [
        ("", "", []),
        ("a", "a", [0]),
        ("foobar", "o", [1, 2]),
        ("bar bar bar bar", "bar", [0, 4, 8, 12]),
    ],
)
def test__templater_python_findall(mainstr, substr, positions):
    """Test _findall."""
    assert list(PythonTemplater._findall(substr, mainstr)) == positions


@pytest.mark.parametrize(
    "mainstr,substrings,positions",
    [
        ("", [], []),
        ("a", ["a"], [[0]]),
        ("foobar", ["o", "b"], [[1, 2], [3]]),
        ("bar foo bar foo", ["bar", "foo"], [[0, 8], [4, 12]]),
    ],
)
def test__templater_python_substring_occurances(mainstr, substrings, positions):
    """Test _findall."""
    occurances = PythonTemplater._substring_occurances(mainstr, substrings)
    assert isinstance(occurances, dict)
    pos_test = [occurances[substring] for substring in substrings]
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
def test__templater_python_sorted_occurance_tuples(test, result):
    """Test _findall."""
    assert PythonTemplater._sorted_occurance_tuples(test) == result


@pytest.mark.parametrize(
    "test,result",
    [
        ("", []),
        ("foo", [("foo", "literal", 0)]),
        (
            "foo {bar} z {{ y",
            [
                ("foo ", "literal", 0),
                ("{bar}", "templated", 4),
                (" z ", "literal", 9),
                ("{{", "escaped", 12),
                (" y", "literal", 14),
            ],
        ),
    ],
)
def test__templater_python_slice_template(test, result):
    """Test _findall."""
    resp = list(PythonTemplater._slice_template(test))
    # check contigious
    assert "".join(elem[0] for elem in resp) == test
    # check indices
    idx = 0
    for literal, _, pos in resp:
        assert pos == idx
        idx += len(literal)
    # Check total result
    assert resp == result


@pytest.mark.parametrize(
    "raw_sliced,literals,raw_occurances,templated_occurances,result",
    [
        ([], [], {}, {}, []),
        (
            [("foo", "literal", 0)],
            ["foo"],
            {"foo": [0]},
            {"foo": [0]},
            [
                (
                    "invariant",
                    slice(0, 3, None),
                    slice(0, 3, None),
                    ("foo", "literal", 0),
                )
            ],
        ),
    ],
)
def test__templater_python_split_invariants(
    raw_sliced, literals, raw_occurances, templated_occurances, result
):
    """Test _findall."""
    resp = PythonTemplater._split_invariants(
        raw_sliced, literals, raw_occurances, templated_occurances
    )
    # check result
    assert resp == result


@pytest.mark.parametrize(
    "split_file,raw_occurances,templated_occurances,result",
    [
        ([], {}, {}, []),
        (
            [
                (
                    "invariant",
                    slice(0, 3, None),
                    slice(0, 3, None),
                    ("foo", "literal", 0),
                )
            ],
            {"foo": [0]},
            {"foo": [0]},
            [("literal", slice(0, 3, None), slice(0, 3, None))],
        ),
        (
            [
                (
                    "invariant",
                    slice(0, 7, None),
                    slice(0, 7, None),
                    ("SELECT ", "literal", 0),
                ),
                (
                    "compound",
                    slice(7, 24, None),
                    slice(7, 22, None),
                    [
                        ("{blah}", "templated", 7),
                        (", ", "literal", 13),
                        ("{foo:.2f}", "templated", 15),
                    ],
                ),
                (
                    "invariant",
                    slice(24, 33, None),
                    slice(22, 31, None),
                    (" as foo, ", "literal", 22),
                ),
                (
                    "simple",
                    slice(33, 38, None),
                    slice(31, 35, None),
                    ("{bar}", "templated", 33),
                ),
                (
                    "invariant",
                    slice(38, 41, None),
                    slice(35, 38, None),
                    (", '", "literal", 35),
                ),
                (
                    "compound",
                    slice(41, 45, None),
                    slice(38, 40, None),
                    [("{{", "escaped", 41), ("}}", "escaped", 43)],
                ),
                (
                    "invariant",
                    slice(45, 76, None),
                    slice(40, 71, None),
                    ("' as convertable from something", "literal", 40),
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
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("templated", slice(7, 13, None), slice(7, 14, None)),
                ("literal", slice(13, 15, None), slice(14, 16, None)),
                ("templated", slice(15, 24, None), slice(16, 22, None)),
                ("literal", slice(24, 33, None), slice(22, 31, None)),
                ("literal", slice(33, 38, None), slice(31, 35, None)),
                ("literal", slice(38, 41, None), slice(35, 38, None)),
                ("escaped", slice(41, 45, None), slice(38, 40, None)),
                ("literal", slice(45, 76, None), slice(40, 71, None)),
            ],
        ),
    ],
)
def test__templater_python_split_uniques_coalesce_rest(
    split_file, raw_occurances, templated_occurances, result
):
    """Test _findall."""
    resp = list(
        PythonTemplater._split_uniques_coalesce_rest(
            split_file,
            raw_occurances,
            templated_occurances,
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
    "raw_file,templated_file,result",
    [
        ("", "", []),
        ("foo", "foo", [("literal", slice(0, 3, None), slice(0, 3, None))]),
        (
            "SELECT {blah}, {foo:.2f} as foo, {bar}, '{{}}' as convertable from something",
            "SELECT nothing, 435.24 as foo, spam, '{}' as convertable from something",
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("templated", slice(7, 13, None), slice(7, 14, None)),
                ("literal", slice(13, 15, None), slice(14, 16, None)),
                ("templated", slice(15, 24, None), slice(16, 22, None)),
                ("literal", slice(24, 33, None), slice(22, 31, None)),
                ("literal", slice(33, 38, None), slice(31, 35, None)),
                ("literal", slice(38, 41, None), slice(35, 38, None)),
                ("escaped", slice(41, 45, None), slice(38, 40, None)),
                ("literal", slice(45, 76, None), slice(40, 71, None)),
            ],
        ),
    ],
)
def test__templater_python_slice_file(raw_file, templated_file, result):
    """Test _findall."""
    resp = list(
        PythonTemplater.slice_file(
            raw_file,
            templated_file,
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
