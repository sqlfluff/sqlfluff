"""Tests for dict helpers."""

import doctest

import sqlfluff.core.helpers.dict as dict_module
from sqlfluff.core.helpers.dict import (
    dict_diff,
    iter_records_from_nested_dict,
    nested_combine,
)


def test_helpers_dict_doctests():
    """Run dict helper doctests.

    Doctests are important for coverage in this module, and coverage isn't currently
    picked up when we run the doctests via --doctests. That means in this case we
    run them directly here.
    https://stackoverflow.com/questions/45261772/how-to-make-pythons-coverage-library-include-doctests
    """
    doctest.testmod(dict_module)


def test__helpers_dict__nested_combine():
    """Test combination of two config dicts."""
    a = {"a": {"b": {"c": 123, "d": 456}}}
    b = {"b": {"b": {"c": 123, "d": 456}}}
    c = {"a": {"b": {"c": 234, "e": 456}}}
    r = nested_combine(a, b, c)
    assert r == {
        "a": {"b": {"c": 234, "e": 456, "d": 456}},
        "b": {"b": {"c": 123, "d": 456}},
    }


def test__helpers_dict__nested_combine_copy_effect():
    """Verify that nested_combine effectively copies dicts.

    In particular it's important that even nested dicts are fully
    isolated, as if not true it can create some very difficult to
    trace bugs.
    """
    # Set up the original dicts.
    a = {"a": {"b": {"c": 123, "d": 456}}}
    b = {"a": {"b": {"c": 234, "e": 567}}, "f": {"g": {"h": "i"}}}
    r = nested_combine(a, b)
    # After combination, edit both some of the inputs and one of the outputs.
    a["a"]["b"]["d"] = 999
    b["f"]["g"]["h"] = "j"
    r["a"]["b"]["e"] = 888
    # Check that editing the result didn't change the input:
    assert b["a"]["b"]["e"] == 567  # and not 888
    # Check that editing the input didn't change the result:
    assert r["a"]["b"]["d"] == 456  # and not 999
    assert r["f"]["g"]["h"] == "i"  # and not "j"


def test__helpers_dict__dict_diff():
    """Test diffs between two config dicts."""
    a = {"a": {"b": {"c": 123, "d": 456, "f": 6}}}
    b = {"b": {"b": {"c": 123, "d": 456}}}
    c = {"a": {"b": {"c": 234, "e": 456, "f": 6}}}
    assert dict_diff(a, b) == a
    assert dict_diff(a, c) == {"a": {"b": {"c": 123, "d": 456}}}
    assert dict_diff(c, a) == {"a": {"b": {"c": 234, "e": 456}}}


def test__config__iter_records_from_nested_dict():
    """Test conversion from nested dict to records."""
    c = iter_records_from_nested_dict({"a": {"b": {"c": 123, "d": 456}, "f": 6}})
    assert list(c) == [
        (("a", "b", "c"), 123),
        (("a", "b", "d"), 456),
        (("a", "f"), 6),
    ]
