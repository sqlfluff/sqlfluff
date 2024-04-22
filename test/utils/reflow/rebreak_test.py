"""Tests for rebreak methods.

Specifically:
- ReflowSequence.rebreak()
"""

import logging

import pytest

from sqlfluff.core import Linter
from sqlfluff.utils.reflow.sequence import ReflowSequence


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).root_variant().tree


@pytest.mark.parametrize(
    "raw_sql_in,raw_sql_out",
    [
        # Trivial Case
        ("select 1", "select 1"),
        # These rely on the default config being for leading operators
        ("select 1\n+2", "select 1\n+2"),
        ("select 1+\n2", "select 1\n+ 2"),  # NOTE: Implicit respace.
        ("select\n  1 +\n  2", "select\n  1\n  + 2"),
        ("select\n  1 +\n  -- comment\n  2", "select\n  1\n  -- comment\n  + 2"),
        # These rely on the default config being for trailing commas
        ("select a,b", "select a,b"),
        ("select a\n,b", "select a,\nb"),
        ("select\n  a\n  , b", "select\n  a,\n  b"),
        ("select\n    a\n    , b", "select\n    a,\n    b"),
        ("select\n  a\n    , b", "select\n  a,\n    b"),
        ("select\n  a\n  -- comment\n  , b", "select\n  a,\n  -- comment\n  b"),
    ],
)
def test_reflow__sequence_rebreak_root(raw_sql_in, raw_sql_out, default_config, caplog):
    """Test the ReflowSequence.rebreak() method directly.

    Focused around a whole segment.
    """
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    for idx, elem in enumerate(seq.elements):
        print(idx, elem)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        new_seq = seq.rebreak()

    print(new_seq.get_fixes())
    assert new_seq.get_raw() == raw_sql_out


@pytest.mark.parametrize(
    "raw_sql_in,target_idx,seq_sql_in,seq_sql_out",
    [
        ("select 1+\n(2+3)", 4, "1+\n(", "1\n+ ("),
        ("select a,\n(b+c)", 4, "a,\n(", "a,\n("),
        ("select a\n  , (b+c)", 6, "a\n  , (", "a,\n  ("),
        # Here we don't have enough context to rebreak it so
        # it should be left unaltered.
        ("select a,\n(b+c)", 6, ",\n(b", ",\n(b"),
        # This intentionally targets an incomplete span.
        ("select a<=b", 4, "a<=", "a<="),
    ],
)
def test_reflow__sequence_rebreak_target(
    raw_sql_in, target_idx, seq_sql_in, seq_sql_out, default_config, caplog
):
    """Test the ReflowSequence.rebreak() method directly.

    Focused around a target segment. This intentionally
    stretches some of the span logic.
    """
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    target = root.raw_segments[target_idx]
    print("Target: ", target)
    seq = ReflowSequence.from_around_target(target, root, config=default_config)
    for idx, elem in enumerate(seq.elements):
        print(idx, elem)
    assert seq.get_raw() == seq_sql_in

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        new_seq = seq.rebreak()

    print(new_seq.get_fixes())
    assert new_seq.get_raw() == seq_sql_out
