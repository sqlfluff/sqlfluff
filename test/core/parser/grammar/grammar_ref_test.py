"""Test the Ref grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Ref


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


def test__parser__grammar_ref_exclude(generate_test_segments, fresh_ansi_dialect):
    """Test the Ref grammar exclude option."""
    ni = Ref("NakedIdentifierSegment", exclude=Ref.keyword("ABS"))
    ts = generate_test_segments(["ABS", "ABSOLUTE"])
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Asset ABS does not match, due to the exclude
    assert not ni.match([ts[0]], parse_context=ctx)
    # Asset ABSOLUTE does match
    assert ni.match([ts[1]], parse_context=ctx)
