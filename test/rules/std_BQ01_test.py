"""Tests for the bigquery BQ01 rule."""

from types import SimpleNamespace

from sqlfluff.rules.bigquery.BQ01 import Rule_BQ01


def _rule() -> Rule_BQ01:
    """Build the rule with its opt-in flag on."""
    return Rule_BQ01(
        code="BQ01",
        description="Forbid BigQuery WITH expressions.",
        forbid_with_expressions=True,
    )


def _context(dialect: str) -> SimpleNamespace:
    """Build the part of a rule context BQ01 reads."""
    return SimpleNamespace(
        dialect=SimpleNamespace(name=dialect),
        segment=object(),
    )


def test_eval_flags_a_with_expression_in_bigquery():
    """A WITH expression in bigquery is reported."""
    rule = _rule()
    context = _context("bigquery")

    result = rule._eval(context)

    assert result is not None
    assert result.anchor is context.segment


def test_eval_ignores_a_with_expression_outside_bigquery():
    """The dialect guard keeps the rule off every other dialect."""
    # ``with_expression`` only exists in the bigquery dialect, so the guard
    # cannot be reached through a linter run. Exercise it directly.
    assert _rule()._eval(_context("postgres")) is None


def test_eval_is_a_noop_when_the_flag_is_off():
    """The rule is opt-in and does nothing by default."""
    rule = _rule()
    rule.forbid_with_expressions = False

    assert rule._eval(_context("bigquery")) is None
