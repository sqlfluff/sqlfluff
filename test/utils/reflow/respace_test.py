"""Tests for respacing methods.

These are mostly on the ReflowPoint class.
"""

import logging

import pytest

from sqlfluff.core import Linter
from sqlfluff.utils.reflow.elements import ReflowPoint
from sqlfluff.utils.reflow.helpers import fixes_from_results
from sqlfluff.utils.reflow.sequence import ReflowSequence


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).root_variant().tree


@pytest.mark.parametrize(
    "raw_sql_in,kwargs,raw_sql_out",
    [
        # Basic cases
        ("select 1+2", {}, "select 1 + 2"),
        ("select    1   +   2    ", {}, "select 1 + 2"),
        # Check newline handling
        ("select\n    1   +   2", {}, "select\n    1 + 2"),
        ("select\n  1   +   2", {}, "select\n  1 + 2"),
        ("select\n  1   +   2", {"strip_newlines": True}, "select 1 + 2"),
        # Check filtering
        ("select  \n  1   +   2 \n ", {}, "select\n  1 + 2\n"),
        ("select  \n  1   +   2 \n ", {"filter": "all"}, "select\n  1 + 2\n"),
        ("select  \n  1   +   2 \n ", {"filter": "inline"}, "select  \n  1 + 2 \n "),
        ("select  \n  1   +   2 \n ", {"filter": "newline"}, "select\n  1   +   2\n"),
    ],
)
def test_reflow__sequence_respace(
    raw_sql_in, kwargs, raw_sql_out, default_config, caplog
):
    """Test the ReflowSequence.respace() method directly."""
    root = parse_ansi_string(raw_sql_in, default_config)
    seq = ReflowSequence.from_root(root, config=default_config)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        new_seq = seq.respace(**kwargs)

    assert new_seq.get_raw() == raw_sql_out


@pytest.mark.parametrize(
    "raw_sql_in,point_idx,kwargs,raw_point_sql_out,fixes_out",
    [
        # Basic cases
        ("select    1", 1, {}, " ", {("replace", "    ")}),
        ("select 1+2", 3, {}, " ", {("create_after", "1")}),
        ("select (1+2)", 3, {}, "", set()),
        ("select (  1+2)", 3, {}, "", {("delete", "  ")}),
        # Newline handling
        ("select\n1", 1, {}, "\n", set()),
        ("select\n  1", 1, {}, "\n  ", set()),
        ("select  \n  1", 1, {}, "\n  ", {("delete", "  ")}),
        (
            "select  \n 1",
            1,
            {"strip_newlines": True},
            " ",
            {("delete", "\n"), ("delete", " "), ("replace", "  ")},
        ),
        (
            "select ( \n  1)",
            3,
            {"strip_newlines": True},
            "",
            {("delete", "\n"), ("delete", " "), ("delete", "  ")},
        ),
    ],
)
def test_reflow__point_respace_point(
    raw_sql_in, point_idx, kwargs, raw_point_sql_out, fixes_out, default_config, caplog
):
    """Test the ReflowPoint.respace_point() method directly.

    NOTE: This doesn't check any pre-existing fixes.
    That should be a separate more specific test.
    """
    root = parse_ansi_string(raw_sql_in, default_config)
    seq = ReflowSequence.from_root(root, config=default_config)
    pnt = seq.elements[point_idx]
    assert isinstance(pnt, ReflowPoint)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        results, new_pnt = pnt.respace_point(
            prev_block=seq.elements[point_idx - 1],
            next_block=seq.elements[point_idx + 1],
            root_segment=root,
            lint_results=[],
            **kwargs,
        )

    assert new_pnt.raw == raw_point_sql_out
    # NOTE: We use set comparison, because ordering isn't important for fixes.
    assert {
        (fix.edit_type, fix.anchor.raw) for fix in fixes_from_results(results)
    } == fixes_out
