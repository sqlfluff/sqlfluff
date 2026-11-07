"""Tests for the StandaloneLineMatcher grammar."""

import pytest

from sqlfluff.core.parser import CommentSegment, StringParser, SymbolSegment
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.standalone import StandaloneLineMatcher


@pytest.fixture
def slash_matcher() -> StandaloneLineMatcher:
    """A matcher for a slash which has to stand alone on its line."""
    return StandaloneLineMatcher(StringParser("/", SymbolSegment, type="slash"))


@pytest.fixture
def ctx(fresh_ansi_dialect) -> ParseContext:
    """A minimal parse context for the standalone matcher tests."""
    return ParseContext(dialect=fresh_ansi_dialect, max_parse_depth=0)


@pytest.mark.parametrize(
    "seeds,idx",
    [
        # Slash alone between two newlines.
        (["a", " ", "\n", "/", "\n", "b"], 3),
        # Leading and trailing whitespace on the line is fine.
        (["\n", "  ", "/", "\t", "\n"], 2),
        # Meta segments (e.g. Indent) are not code, so they're ignored.
        (["\n", "<indent>", "/", "<dedent>", "\n"], 2),
        # The very first line of a file counts as a line start.
        (["/", "\n", "b"], 0),
        # The very last line of a file counts as a line end.
        (["a", "\n", "/"], 2),
    ],
)
def test_standalone_line_matcher_matches(
    generate_test_segments, slash_matcher, ctx, seeds, idx
):
    """A slash which is the only code on its line should match."""
    segments = generate_test_segments(seeds)
    match = slash_matcher.match(segments, idx, ctx)
    assert match
    assert match.matched_slice == slice(idx, idx + 1)


@pytest.mark.parametrize(
    "seeds,idx",
    [
        # Something before the slash on the same line.
        (["a", " ", "/", " ", "b"], 2),
        # Something after the slash on the same line.
        (["\n", "/", " ", "b"], 1),
        # The inner matcher itself doesn't match.
        (["\n", "*", "\n"], 1),
    ],
)
def test_standalone_line_matcher_no_match(
    generate_test_segments, slash_matcher, ctx, seeds, idx
):
    """A slash which shares its line with other code should not match."""
    segments = generate_test_segments(seeds)
    assert not slash_matcher.match(segments, idx, ctx)


def _generate_segments_with_comment(generate_test_segments, seeds, elem):
    """Generate segments, replacing block comments with a CommentSegment.

    ``generate_test_segments`` already emits inline ``--`` comments. It does
    not recognise block comments, so only that form needs replacing here.
    """
    segments = list(generate_test_segments(seeds))
    if elem.startswith("--"):
        return segments
    idx = seeds.index(elem)
    original = segments[idx]
    segments[idx] = CommentSegment(original.raw, pos_marker=original.pos_marker)
    return segments


@pytest.mark.parametrize(
    "seeds,idx",
    [
        # A trailing inline comment occupies the delimiter's line.
        (["\n", "/", " ", "-- note", "\n"], 1),
        # A leading block comment also occupies the delimiter's line.
        (["\n", "/* note */", " ", "/", "\n"], 3),
    ],
)
def test_standalone_line_matcher_rejects_comments(
    generate_test_segments, slash_matcher, ctx, seeds, idx
):
    """A delimiter sharing its line with a comment is not standalone."""
    comment = next(elem for elem in seeds if "note" in elem)
    segments = _generate_segments_with_comment(generate_test_segments, seeds, comment)
    assert not slash_matcher.match(segments, idx, ctx)


def test_standalone_line_matcher_returns_inner_match(
    generate_test_segments, slash_matcher, ctx
):
    """The inner match (including any meta segments) is passed straight through."""
    segments = generate_test_segments(["\n", "/", "\n"])
    match = slash_matcher.match(segments, 1, ctx)
    assert match.matched_slice == slice(1, 2)
    assert not match.insert_segments
    assert not match.child_matches


def test_standalone_line_matcher_simple(slash_matcher, ctx):
    """The simple hint is delegated to the inner matcher."""
    assert slash_matcher.simple(ctx) == (frozenset({"/"}), frozenset())


def test_standalone_line_matcher_is_not_optional(slash_matcher):
    """A standalone matcher is never optional."""
    assert not slash_matcher.is_optional()


def test_standalone_line_matcher_cache_key(slash_matcher):
    """The cache key includes the inner matcher's key."""
    assert (
        slash_matcher.cache_key()
        == "standalone-line-" + slash_matcher.matcher.cache_key()
    )


def test_standalone_line_matcher_cache_key_with_keywords():
    """Configured resume keywords are part of the cache key, in sorted order."""
    lenient = StandaloneLineMatcher(
        StringParser("/", SymbolSegment, type="slash"),
        resume_keywords=("SELECT", "create"),
    )
    assert lenient.cache_key() == (
        "standalone-line-" + lenient.matcher.cache_key() + "-CREATE,SELECT"
    )
    # An empty keyword set leaves the strict key unchanged.
    strict = StandaloneLineMatcher(
        StringParser("/", SymbolSegment, type="slash"), resume_keywords=()
    )
    assert strict.cache_key() == "standalone-line-" + strict.matcher.cache_key()


@pytest.mark.parametrize(
    "seeds,idx,keywords,expected",
    [
        # The comment ends the file, so the delimiter line cannot continue.
        (["\n", "/", " ", "-- note"], 1, ("CREATE",), True),
        # Only blank lines and comments remain after the comment.
        (["\n", "/", " ", "-- note", "\n", "\n", "  ", "\n"], 1, ("CREATE",), True),
        # A non-comment token on the delimiter's line is never a statement end.
        (["\n", "/", " ", "b", "\n"], 1, ("CREATE",), False),
        # The next line starts a statement.
        (["\n", "/", " ", "-- note", "\n", "CREATE"], 1, ("CREATE",), True),
        # Blank and comment-only lines between the delimiter and the statement.
        (
            ["\n", "/", " ", "-- note", "\n", "\n", "-- more", "\n", "SELECT"],
            1,
            ("SELECT",),
            True,
        ),
        # The comment is not the last thing on its line.
        (["\n", "/", " ", "-- note", " ", "b", "\n"], 1, ("CREATE",), False),
        # The next line continues the expression instead of starting a statement.
        (["\n", "/", " ", "-- note", "\n", "b"], 1, ("CREATE",), False),
        # Without configured keywords a trailing comment is always rejected.
        (["\n", "/", " ", "-- note", "\n", "CREATE"], 1, (), False),
    ],
)
def test_standalone_line_matcher_comment_lookahead(
    generate_test_segments, ctx, seeds, idx, keywords, expected
):
    """A configured matcher only accepts a comment before a new statement."""
    segments = generate_test_segments(seeds)
    matcher = StandaloneLineMatcher(
        StringParser("/", SymbolSegment, type="slash"), resume_keywords=keywords
    )
    assert bool(matcher.match(segments, idx, ctx)) is expected
