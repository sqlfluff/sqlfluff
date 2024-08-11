"""Tests pickling and unpickling of errors."""

import copy
import pickle

import pytest

from sqlfluff.core.errors import SQLBaseError, SQLLexError, SQLLintError, SQLParseError
from sqlfluff.core.parser import PositionMarker, RawSegment
from sqlfluff.core.rules import BaseRule
from sqlfluff.core.templaters import TemplatedFile


class Rule_T078(BaseRule):
    """A dummy rule."""

    groups = ("all",)

    def _eval(self, context):
        pass


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
