"""Tests for respacing methods.

These are mostly on the ReflowPoint class.
"""

import logging

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.utils.reflow.elements import ReflowPoint
from sqlfluff.utils.reflow.helpers import fixes_from_results
from sqlfluff.utils.reflow.respace import process_spacing
from sqlfluff.utils.reflow.sequence import ReflowSequence


def test_reflow__process_spacing_duplicate_whitespace_fix_anchors():
    """Each duplicate-whitespace fix must anchor the whitespace it removes.

    The "Removing duplicate whitespace" fixes anchored the leaked loop variable
    (the last segment of the buffer) instead of each ``ws`` being removed, so
    for three adjacent whitespaces both deletes targeted the final segment and
    the middle one was never fixed.
    """
    w1, w2, w3 = WhitespaceSegment(" "), WhitespaceSegment(" "), WhitespaceSegment(" ")
    buffer, _, results = process_spacing([w1, w2, w3], strip_newlines=False)

    # w1 is kept; w2 and w3 are pruned from the returned buffer.
    assert len(buffer) == 1 and buffer[0] is w1
    # Each pruned whitespace is the anchor of exactly one delete fix, and the
    # kept one is never targeted.
    anchors = [fix.anchor for result in results for fix in result.fixes]
    assert sum(anchor is w2 for anchor in anchors) == 1
    assert sum(anchor is w3 for anchor in anchors) == 1
    assert all(anchor is not w1 for anchor in anchors)


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).tree


def test_reflow__respace_does_not_strip_newline_before_comment():
    """A newline directly before a comment must survive strip_newlines=True.

    Regression test: when a parent constraint (e.g. `spacing_within =
    single:inline` on `expression`) requests stripped newlines between a
    binary operator like `AND` and the following token, and that following
    token is a comment, the newline separating them must NOT be removed.
    Removing it would glue the operator to the `--` comment marker and
    change the meaning/formatting of the statement.
    """
    config = FluffConfig(
        overrides={"dialect": "ansi"},
        configs={
            "layout": {"type": {"expression": {"spacing_within": "single:inline"}}}
        },
    )
    sql = "SELECT * FROM t WHERE a AND\n-- comment\nb\n"
    root = parse_ansi_string(sql, config)
    seq = ReflowSequence.from_root(root, config=config)
    new_seq = seq.respace()
    assert new_seq.get_raw() == sql


def test_reflow__respace_align_ignores_predecessor_on_another_line():
    """Aligning must ignore a preceding code segment from an earlier line.

    Regression test for #8256. With leading commas and the T-SQL ``=`` alias
    syntax, the first aliased column is the first code on its line, so the
    code preceding it is the trailing token of an *earlier* line (``SELECT``).
    Its column bore no relation to where that alias starts, but it was still
    counted when picking the alignment target, inflating the target column and
    padding every *other* line to match. That produced two spaces after the
    leading comma on aliased rows while non-aliased rows kept one.

    The commas must keep a single following space; alignment is achieved by
    padding before the ``=`` instead.
    """
    config = FluffConfig(
        overrides={"dialect": "tsql"},
        configs={
            "layout": {
                "type": {
                    "comma": {"line_position": "leading"},
                    "alias_operator": {
                        "spacing_before": "align",
                        "align_within": "select_clause",
                        "align_scope": "bracketed",
                    },
                    "alias_expression": {
                        "spacing_before": "align",
                        "align_within": "select_clause",
                        "align_scope": "bracketed",
                    },
                }
            }
        },
    )
    sql = (
        "SELECT\n"
        "    FirstCol = 'a'\n"
        "    , SecondCol = 'b'\n"
        "    , ThirdCol = 'c'\n"
        "    , t.NonaliasedCol\n"
        "FROM TestTable AS t\n"
    )
    linter = Linter(config=config)
    root = linter.parse_string(sql).tree
    seq = ReflowSequence.from_root(root, config=config)
    result = seq.respace().get_raw()

    # Every leading comma keeps exactly one following space.
    assert ",  " not in result
    # Alignment is still achieved, via padding before the `=`.
    operator_columns = {line.index("=") for line in result.splitlines() if "=" in line}
    assert len(operator_columns) == 1


def test_reflow__respace_handles_zero_length_blocks():
    """A zero length block next to a `touch` constraint must not raise.

    Regression test: placeholders render to an empty raw. Their spacing
    defaults to `any`, but that is user configurable, so the check for a
    would-be `--` comment marker must not assume that both sides of the
    point have at least one character to inspect.
    """
    config = FluffConfig(
        overrides={"dialect": "ansi", "templater": "jinja"},
        configs={
            "layout": {
                "type": {
                    "placeholder": {
                        "spacing_before": "touch",
                        "spacing_after": "touch",
                    }
                }
            }
        },
    )
    sql = "SELECT 1 + {{ '' }} 2\n"
    root = parse_ansi_string(sql, config)
    seq = ReflowSequence.from_root(root, config=config)
    # The placeholder has no characters of its own, so it can't build a
    # marker either side of it and the spacing is resolved as normal.
    assert seq.respace().get_raw() == "SELECT 1 +2\n"


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
