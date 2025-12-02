"""Test the Ref grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.dialects import Dialect
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Ref
from sqlfluff.core.parser.lexer import RegexLexer
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.parsers import StringParser
from sqlfluff.core.parser.segments import CodeSegment, WhitespaceSegment


@pytest.fixture(scope="function")
def test_dialect():
    """A stripped back test dialect for testing."""
    test_dialect = Dialect("test", root_segment_name="FileSegment")
    test_dialect.set_lexer_matchers(
        [
            RegexLexer("whitespace", r"[^\S\r\n]+", WhitespaceSegment),
            RegexLexer(
                "code", r"[0-9a-zA-Z_]+", CodeSegment, segment_kwargs={"type": "code"}
            ),
        ]
    )
    test_dialect.add(FooSegment=StringParser("foo", CodeSegment, type="foo"))
    # Return the expanded copy.
    return test_dialect.expand()


def test__parser__grammar__ref_eq():
    """Test equality of Ref Grammars."""
    r1 = Ref("foo")
    r2 = Ref("foo")
    assert r1 is not r2
    assert r1 == r2
    check_list = [1, 2, r2, 3]
    # Check we can find it in lists
    assert r1 in check_list
    # Check we can get it's position
    assert check_list.index(r1) == 2
    # Check we can remove it from a list
    check_list.remove(r1)
    assert r1 not in check_list


def test__parser__grammar__ref_repr():
    """Test the __repr__ method of Ref."""
    assert repr(Ref("foo")) == "<Ref: 'foo'>"
    assert repr(Ref("bar", optional=True)) == "<Ref: 'bar' [opt]>"


def test__parser__grammar_ref_match(generate_test_segments, test_dialect):
    """Test the Ref grammar match method."""
    foo_ref = Ref("FooSegment")
    test_segments = generate_test_segments(["bar", "foo", "bar"])
    ctx = ParseContext(dialect=test_dialect)

    match = foo_ref.match(test_segments, 1, ctx)

    assert match == MatchResult(
        matched_slice=slice(1, 2),
        matched_class=CodeSegment,
        segment_kwargs={"instance_types": ("foo",)},
    )


def test__parser__grammar_ref_exclude(generate_test_segments, fresh_ansi_dialect):
    """Test the Ref grammar exclude option with the match method."""
    identifier = Ref("NakedIdentifierSegment", exclude=Ref.keyword("ABS"))
    test_segments = generate_test_segments(["ABS", "ABSOLUTE"])
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Assert ABS does not match, due to the exclude
    assert not identifier.match(test_segments, 0, ctx)
    # Assert ABSOLUTE does match
    assert identifier.match(test_segments, 1, ctx)
