"""Tests pickling and unpickling of errors."""

import copy
import pickle

import pytest

from sqlfluff.core.errors import SQLBaseError, SQLLexError, SQLLintError, SQLParseError
from sqlfluff.core.parser import PositionMarker, RawSegment
from sqlfluff.core.rules import BaseRule
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice


class Rule_T078(BaseRule):
    """A dummy rule."""

    groups = ("all",)

    def _eval(self, context):
        pass


@pytest.mark.parametrize("error_class", [SQLParseError, SQLLintError])
@pytest.mark.parametrize("slice_type", ["literal", "templated"])
@pytest.mark.parametrize("source_slice", [slice(2, 7), slice(2, 2)])
def test__error_source_positions(error_class, slice_type, source_slice):
    """Serialize source coordinates regardless of whether a span is literal."""
    source = "a\nbc\ndef"
    template = TemplatedFile(
        source,
        fname="<string>",
        sliced_file=[TemplatedFileSlice(slice_type, slice(0, 8), slice(0, 8))],
        raw_sliced=[RawFileSlice(source, slice_type, 0)],
    )
    segment = RawSegment(
        source[source_slice], PositionMarker(source_slice, source_slice, template)
    )
    kwargs = {"rule": Rule_T078} if error_class is SQLLintError else {}
    result = error_class("Foo", segment=segment, **kwargs).to_dict()
    expected = {
        "start_line_no": 2,
        "start_line_pos": 1,
        "start_file_pos": 2,
        "end_line_no": 3 if source_slice.stop == 7 else 2,
        "end_line_pos": 3 if source_slice.stop == 7 else 1,
        "end_file_pos": source_slice.stop,
    }
    assert {key: result[key] for key in expected} == expected


def test__parse_error_without_segment_positions():
    """Errors without a source segment retain their supplied start position."""
    result = SQLParseError("Foo", line_no=2, line_pos=3).to_dict()
    assert result["start_line_no"] == 2
    assert result["start_line_pos"] == 3
    assert "start_file_pos" not in result
    assert "end_file_pos" not in result


def assert_pickle_robust(err: SQLBaseError):
    """Test that the class remains the same through copying and pickling."""
    # First try copying (and make sure they still compare equal)
    err_copy = copy.copy(err)
    assert err_copy == err
    # Then try picking (and make sure they also still compare equal)
    pickled = pickle.dumps(err)
    pickle_copy = pickle.loads(pickled)
    assert pickle_copy == err


@pytest.mark.parametrize(
    "ignore",
    [True, False],
)
def test__lex_error_pickle(ignore):
    """Test lexing error pickling."""
    template = TemplatedFile.from_string("foobar")
    err = SQLLexError("Foo", pos=PositionMarker(slice(0, 6), slice(0, 6), template))
    # Set ignore to true if configured.
    # NOTE: This not copying was one of the reasons for this test.
    err.ignore = ignore
    assert_pickle_robust(err)


@pytest.mark.parametrize(
    "ignore",
    [True, False],
)
def test__parse_error_pickle(ignore):
    """Test parse error pickling."""
    template = TemplatedFile.from_string("foobar")
    segment = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    err = SQLParseError("Foo", segment=segment)
    # Set ignore to true if configured.
    # NOTE: This not copying was one of the reasons for this test.
    err.ignore = ignore
    assert_pickle_robust(err)


@pytest.mark.parametrize(
    "ignore",
    [True, False],
)
def test__lint_error_pickle(ignore):
    """Test lint error pickling."""
    template = TemplatedFile.from_string("foobar")
    segment = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    err = SQLLintError("Foo", segment=segment, rule=Rule_T078)
    # Set ignore to true if configured.
    # NOTE: This not copying was one of the reasons for this test.
    err.ignore = ignore
    assert_pickle_robust(err)
