"""Tests for CV13 (string concatenation) covering defensive edge cases.

These tests exercise code paths that are not reachable through normal SQL
parsing but exist as defensive guards:
- Line 70: ``continue`` when ``left is None or right is None``
- Line 102: ``return None`` at the end of ``_find_non_whitespace``
"""

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser import (
    NewlineSegment,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import RuleContext
from sqlfluff.rules.convention.CV13 import Rule_CV13, _find_non_whitespace

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeExpression:
    """Minimal stand-in for an expression segment with custom children."""

    def __init__(self, segments):
        self._segments = tuple(segments)

    def is_type(self, *types):
        return "expression" in types

    @property
    def segments(self):
        return self._segments


def _make_rule():
    return Rule_CV13(code="CV13", description="test")


def _make_context(expression):
    dialect = dialect_selector("ansi")
    config = FluffConfig(overrides={"dialect": "ansi"})
    return RuleContext(
        dialect=dialect,
        fix=True,
        templated_file=None,
        path=None,
        config=config,
        segment=expression,
    )


# ---------------------------------------------------------------------------
# Unit tests for _find_non_whitespace (covers line 102)
# ---------------------------------------------------------------------------


class TestFindNonWhitespace:
    """Unit tests for the ``_find_non_whitespace`` helper."""

    def test_returns_none_when_walking_forward_past_end(self) -> None:
        """Walking forward from the last index yields None."""
        segments = [
            SymbolSegment(raw="+", type="binary_operator"),
        ]
        assert _find_non_whitespace(segments, 0, direction=1) is None

    def test_returns_none_when_walking_backward_past_start(self) -> None:
        """Walking backward from index 0 yields None."""
        segments = [
            SymbolSegment(raw="+", type="binary_operator"),
        ]
        assert _find_non_whitespace(segments, 0, direction=-1) is None

    def test_returns_none_when_only_whitespace_forward(self) -> None:
        """Walking forward through only whitespace/newline returns None."""
        segments = [
            SymbolSegment(raw="+", type="binary_operator"),
            WhitespaceSegment(raw=" "),
            NewlineSegment(),
            WhitespaceSegment(raw="    "),
        ]
        assert _find_non_whitespace(segments, 0, direction=1) is None

    def test_returns_none_when_only_whitespace_backward(self) -> None:
        """Walking backward through only whitespace/newline returns None."""
        segments = [
            WhitespaceSegment(raw=" "),
            NewlineSegment(),
            WhitespaceSegment(raw="    "),
            SymbolSegment(raw="+", type="binary_operator"),
        ]
        assert _find_non_whitespace(segments, 3, direction=-1) is None

    def test_finds_non_whitespace_forward(self) -> None:
        """Walking forward skips whitespace and finds the target."""
        target = SymbolSegment(raw="x", type="quoted_literal")
        segments = [
            SymbolSegment(raw="+", type="binary_operator"),
            WhitespaceSegment(raw=" "),
            NewlineSegment(),
            target,
        ]
        assert _find_non_whitespace(segments, 0, direction=1) is target

    def test_finds_non_whitespace_backward(self) -> None:
        """Walking backward skips whitespace and finds the target."""
        target = SymbolSegment(raw="x", type="quoted_literal")
        segments = [
            target,
            WhitespaceSegment(raw=" "),
            NewlineSegment(),
            SymbolSegment(raw="+", type="binary_operator"),
        ]
        assert _find_non_whitespace(segments, 3, direction=-1) is target


# ---------------------------------------------------------------------------
# Tests for Rule_CV13._eval with synthetic segments (covers line 70)
# ---------------------------------------------------------------------------


class TestCV13EvalEdgeCases:
    """Test ``_eval`` with crafted expression segments.

    The SQL parser never produces an expression where a ``+``
    binary_operator has no non-whitespace neighbour on one side
    (it would be parsed as a sign_indicator instead). These tests
    construct that scenario directly to exercise the defensive guard
    on line 70 (``continue`` when ``left is None or right is None``).
    """

    def test_skip_plus_with_no_left_neighbour(self) -> None:
        """A ``+`` with only whitespace to its left is silently skipped."""
        expr = _FakeExpression(
            [
                WhitespaceSegment(raw=" "),
                SymbolSegment(raw="+", type="binary_operator"),
                WhitespaceSegment(raw=" "),
                SymbolSegment(raw="'b'", type="quoted_literal"),
            ]
        )
        rule = _make_rule()
        result = rule._eval(_make_context(expr))
        # No violation -- the + is skipped because left is None.
        assert result is None

    def test_skip_plus_with_no_right_neighbour(self) -> None:
        """A ``+`` with only whitespace to its right is silently skipped."""
        expr = _FakeExpression(
            [
                SymbolSegment(raw="'a'", type="quoted_literal"),
                WhitespaceSegment(raw=" "),
                SymbolSegment(raw="+", type="binary_operator"),
                WhitespaceSegment(raw=" "),
            ]
        )
        rule = _make_rule()
        result = rule._eval(_make_context(expr))
        assert result is None

    def test_skip_plus_with_no_neighbours_at_all(self) -> None:
        """A lone ``+`` in an expression is silently skipped."""
        expr = _FakeExpression(
            [
                SymbolSegment(raw="+", type="binary_operator"),
            ]
        )
        rule = _make_rule()
        result = rule._eval(_make_context(expr))
        assert result is None


# ---------------------------------------------------------------------------
# Smoke tests via the public linting API
# ---------------------------------------------------------------------------


class TestCV13Smoke:
    """Smoke tests using ``sqlfluff.lint`` for basic sanity."""

    def test_no_violation_for_numeric_addition(self) -> None:
        """Numeric addition should never be flagged."""
        import sqlfluff

        result = sqlfluff.lint("SELECT 1 + 2", rules=["CV13"])
        assert result == []

    def test_no_violation_for_unary_plus(self) -> None:
        """Unary ``+`` (sign_indicator) is not a binary_operator."""
        import sqlfluff

        result = sqlfluff.lint("SELECT + 'hello'", rules=["CV13"])
        assert result == []
