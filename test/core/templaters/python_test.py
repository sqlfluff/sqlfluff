"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import PythonTemplateInterface
from sqlfluff.core import SQLTemplaterError


PYTHON_STRING = "SELECT * FROM {blah}"


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplateInterface(override_context=dict(blah="foo"))
    instr = PYTHON_STRING
    outstr, _ = t.process(instr)
    assert str(outstr) == "SELECT * FROM foo"


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplateInterface(override_context=dict(noblah="foo"))
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
    assert list(PythonTemplateInterface._findall(substr, mainstr)) == positions


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
    occurances = PythonTemplateInterface._substring_occurances(mainstr, substrings)
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
    assert PythonTemplateInterface._sorted_occurance_tuples(test) == result


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
def test__templater_python_slice_python_template(test, result):
    """Test _findall."""
    resp = PythonTemplateInterface._slice_python_template(test)
    # check contigious
    assert "".join(elem[0] for elem in resp) == test
    # check indices
    idx = 0
    for literal, _, pos in resp:
        assert pos == idx
        idx += len(literal)
    # Check total result
    assert resp == result
