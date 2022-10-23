"""Tests for reindenting methods.

Specifically:
- ReflowPoint.indent_to()
- ReflowPoint.get_indent()
- deduce_line_indent()
"""

import logging
import pytest

from sqlfluff.core import Linter
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.utils.reflow.sequence import ReflowSequence
from sqlfluff.utils.reflow.reindent import (
    deduce_line_indent,
    lint_indent_points,
    _crawl_indent_points,
    _IndentPoint,
)


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).tree


@pytest.mark.parametrize(
    "raw_sql_in,elem_idx,indent_to,point_sql_out",
    [
        # Trivial Case
        ("select\n  1", 1, "  ", "\n  "),
        # Change existing indents
        ("select\n  1", 1, "    ", "\n    "),
        ("select\n  1", 1, " ", "\n "),
        ("select\n1", 1, "  ", "\n  "),
        ("select\n  1", 1, "", "\n"),
        # Create new indents
        ("select 1", 1, "  ", "\n  "),
        ("select 1", 1, " ", "\n "),
        ("select 1", 1, "", "\n"),
        ("select      1", 1, "  ", "\n  "),
    ],
)
def test_reflow__point_indent_to(
    raw_sql_in, elem_idx, indent_to, point_sql_out, default_config, caplog
):
    """Test the ReflowPoint.indent_to() method directly."""
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    elem = seq.elements[elem_idx]
    print("Element: ", elem)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        new_fixes, new_point = elem.indent_to(
            indent_to,
            before=seq.elements[elem_idx - 1].segments[-1],
            after=seq.elements[elem_idx + 1].segments[0],
        )

    print(new_fixes)
    assert new_point.raw == point_sql_out


@pytest.mark.parametrize(
    "raw_sql_in,elem_idx,indent_out",
    [
        # Null case
        ("select 1", 1, None),
        # Trivial Case
        ("select\n  1", 1, "  "),
        # Harder Case (i.e. take the last indent)
        ("select\n \n  \n   1", 1, "   "),
    ],
)
def test_reflow__point_get_indent(
    raw_sql_in, elem_idx, indent_out, default_config, caplog
):
    """Test the ReflowPoint.get_indent() method directly."""
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    elem = seq.elements[elem_idx]
    print("Element: ", elem)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = elem.get_indent()

    assert result == indent_out


@pytest.mark.parametrize(
    "raw_sql_in,target_raw,indent_out",
    [
        # Trivial case
        ("select 1", "select", ""),
        ("select 1", "1", ""),
        # Easy Case
        ("select\n  1", "1", "  "),
        # Harder Cases (i.e. take the last indent)
        ("select\n \n  \n   1", "1", "   "),
        ("select\n \n  \n   1+2+3+4", "4", "   "),
        ("select\n   1 + 2", "2", "   "),
    ],
)
def test_reflow__deduce_line_indent(
    raw_sql_in, target_raw, indent_out, default_config, caplog
):
    """Test the deduce_line_indent() method directly."""
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())

    for target_seg in root.raw_segments:
        if target_seg.raw == target_raw:
            break
    else:
        raise ValueError("Target Raw Not Found")
    print("Target: ", target_seg)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = deduce_line_indent(target_seg, root)

    assert result == indent_out


@pytest.mark.parametrize(
    "raw_sql_in,points_out",
    [
        # Trivial
        (
            "select 1",
            [
                # No point at the start.
                # Point after select (not newline)
                _IndentPoint(
                    idx=1,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=None,
                    is_line_break=False,
                    untaken_indents=(),
                ),
                # Point after 1 (not newline either)
                _IndentPoint(
                    idx=3,
                    indent_impulse=-1,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=None,
                    is_line_break=False,
                    untaken_indents=(1,),
                ),
            ],
        ),
        (
            "\nselect 1\n",
            [
                # Start point
                _IndentPoint(
                    idx=0,
                    indent_impulse=0,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=None,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # Point after select (not newline)
                _IndentPoint(
                    idx=2,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=0,
                    is_line_break=False,
                    untaken_indents=(),
                ),
                # Point after 1 (is newline)
                _IndentPoint(
                    idx=4,
                    indent_impulse=-1,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=0,
                    is_line_break=True,
                    untaken_indents=(1,),
                ),
            ],
        ),
        (
            "select\n1",
            [
                # No point at the start.
                # Point after select (not newline)
                _IndentPoint(
                    idx=1,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=None,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # Point after 1 (is not newline)
                _IndentPoint(
                    idx=3,
                    indent_impulse=-1,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=1,
                    is_line_break=False,
                    untaken_indents=(),
                ),
            ],
        ),
        # More stretching cases.
        (
            "SELECT\n    r.a,\n    s.b\nFROM r\nJOIN s\n    "
            "ON\n        r.a = s.a\n        AND true",
            [
                # No point at the start.
                # After SELECT
                _IndentPoint(
                    idx=1,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=None,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                _IndentPoint(
                    idx=9,
                    indent_impulse=0,
                    indent_trough=0,
                    initial_indent_balance=1,
                    last_line_break_idx=1,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # Before FROM
                _IndentPoint(
                    idx=15,
                    indent_impulse=-1,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=9,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # Untaken indent before "r"
                _IndentPoint(
                    idx=17,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=15,
                    is_line_break=False,
                    untaken_indents=(),
                ),
                # Before JOIN (-1 balance to take us back to
                # baseline (in line with FROM))
                # NOTE: It keeps the untaken indent from the
                # previous point, but shouldn't use it.
                _IndentPoint(
                    idx=19,
                    indent_impulse=-1,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=15,
                    is_line_break=True,
                    untaken_indents=(1,),
                ),
                # Untaken indent before "s"
                _IndentPoint(
                    idx=21,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=0,
                    last_line_break_idx=19,
                    is_line_break=False,
                    untaken_indents=(),
                ),
                # NOTE: this is an interesting one. It's a Dedent-Indent pair.
                # There's a zero balance, and a trough of -1. We carry in the previous
                # untaken indent. But should pass if forward after this.
                _IndentPoint(
                    idx=23,
                    indent_impulse=0,
                    indent_trough=-1,
                    initial_indent_balance=1,
                    last_line_break_idx=19,
                    is_line_break=True,
                    untaken_indents=(1,),
                ),
                # After ON. Default is indented_on_contents = True, so there is
                # an indent here. We *SHOULDNT* have an untaken indent here,
                # because while there was one at the last point, the trough
                # of the last point should have cleared it.
                _IndentPoint(
                    idx=25,
                    indent_impulse=1,
                    indent_trough=0,
                    initial_indent_balance=1,
                    last_line_break_idx=23,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # Before AND
                _IndentPoint(
                    idx=39,
                    indent_impulse=0,
                    indent_trough=0,
                    initial_indent_balance=2,
                    last_line_break_idx=25,
                    is_line_break=True,
                    untaken_indents=(),
                ),
                # after "true"
                _IndentPoint(
                    idx=43,
                    indent_impulse=-2,
                    indent_trough=-2,
                    initial_indent_balance=2,
                    last_line_break_idx=39,
                    is_line_break=False,
                    untaken_indents=(),
                ),
            ],
        ),
        (
            "SELECT *\nFROM t1\nJOIN t2 ON true\nAND true",
            [
                # No point at the start.
                # NOTE: Abbreviated notation given much is the same as above.
                # After SELECT
                _IndentPoint(1, 1, 0, 0, None, False, ()),
                _IndentPoint(3, -1, -1, 1, None, True, (1,)),
                _IndentPoint(5, 1, 0, 0, 3, False, ()),
                _IndentPoint(7, -1, -1, 1, 3, True, (1,)),
                # JOIN
                _IndentPoint(9, 1, 0, 0, 7, False, ()),
                # TRICKY POINT (we're between "t2" and "ON").
                # The indent between Join and t2 wasn't taken, but we're
                # also climbing down from that here. It should be in the
                # untaken indents _here_ but not passed forward. There is
                # however another indent opportunity here which ALSO isn't
                # taken, so that one *should* be passed forward.
                _IndentPoint(11, 0, -1, 1, 7, False, (1,)),
                # TRICKY POINT (we're between "ON" and "true").
                # Default is indented_on_contents = True.
                # This means that there is an additional indent here.
                # It's not taken though. The incoming balance of 1
                # isn't taken yet either (hence a 1 in the untaken indent).
                _IndentPoint(13, 1, 0, 1, 7, False, (1,)),
                # Between "true" and "AND".
                # Balance is 2, but both untaken.
                _IndentPoint(15, 0, 0, 2, 7, True, (1, 2)),
                # End point
                _IndentPoint(19, -2, -2, 2, 15, False, (1, 2)),
            ],
        ),
    ],
)
def test_reflow__crawl_indent_points(raw_sql_in, points_out, default_config, caplog):
    """Test _crawl_indent_points directly."""
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        points = list(_crawl_indent_points(seq.elements))
    assert points == points_out


@pytest.mark.parametrize(
    "raw_sql_in,raw_sql_out",
    [
        # Trivial
        (
            "select 1",
            "select 1",
        ),
        # Initial Indent
        (
            "      select 1",
            "select 1",
        ),
        # Trailing Newline
        (
            "      select 1\n",
            "select 1\n",
        ),
        # Basic Multiline
        (
            "select\n1",
            "select\n  1",
        ),
        # Advanced Multiline
        (
            "select\n1+(\n2+3\n),\n4\nfrom foo",
            "select\n  1+(\n    2+3\n  ),\n  4\nfrom foo",
        ),
        (
            "select\n    1+(\n    2+3\n    ),\n    4\n    from foo",
            "select\n  1+(\n    2+3\n  ),\n  4\nfrom foo",
        ),
        # Multiple untaken indents. We should only indent as many
        # times as required.
        (
            "   select ((((\n1\n))))",
            "select ((((\n  1\n))))",
        ),
        (
            "select (((\n((\n3\n))\n)))",
            "select (((\n  ((\n    3\n  ))\n)))",
        ),
        # ### Templated Multiline Cases ###
        # NOTE: the templated tags won't show here, but they
        # should still be indented.
        # Trailing tag. NOTE: Last tag indented
        (
            "select\n1\n{% if true %}\n+ 2\n{% endif %}",
            "select\n  1\n  \n    + 2\n  ",
        ),
        # Cutting across the parse tree
        (
            "select\n1\n{% if true %}\n,2\nFROM a\n{% endif %}",
            # This set of template tags cuts across the parse
            # tree. We should indent them appropriately. In this case
            # that should mean "case 3", picking the lowest of the
            # existing indents which should mean no indent for either.
            # We also shouldn't indent the contents between them either
            # when taking this option.
            "select\n  1\n\n  ,2\nFROM a\n",
        ),
        # Template tags at file ends
        (
            "{% if true %}\nSELECT 1\n{% endif %}",
            "\n  SELECT 1\n",
        ),
        # Template loops:
        (
            "select\n  0,\n  {% for i in [1, 2, 3] %}\n    {{i}},\n  {% endfor %}\n  4",
            "select\n  0,\n  \n    1,\n  \n    2,\n  \n    3,\n  \n  4",
        ),
        # Correction and handling of hanging indents
        (
            "select 1, 2",
            "select 1, 2",
        ),
        (
            "select 1,\n2",
            "select\n  1,\n  2",
        ),
        (
            "select 1,\n       2",
            "select\n  1,\n  2",
        ),
        # A hanging example where we're modifying a currently empty point.
        (
            "select greatest(1,\n2)",
            "select greatest(\n  1,\n  2\n)",
        ),
        # Test handling of many blank lines.
        # NOTE:
        #    1. Initial whitespace should remain, because it's not an indent.
        #    2. Blank lines should also remain, because they're also not an indent.
        (
            "\n\n  \n\nselect\n\n\n\n    \n\n     1\n\n       \n\n",
            "\n\n  \n\nselect\n\n\n\n    \n\n  1\n\n       \n\n",
        ),
    ],
)
def test_reflow__lint_indent_points(raw_sql_in, raw_sql_out, default_config, caplog):
    """Test the lint_indent_points() method directly.

    Rather than testing directly, for brevity we check
    the raw output it produces. This results in a more
    compact test.
    """
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        elements, fixes = lint_indent_points(seq.elements, single_indent="  ")

    result_raw = "".join(elem.raw for elem in elements)
    assert result_raw == raw_sql_out, "Raw Element Check Failed!"

    # Now we've checked the elements - check that applying the fixes gets us to
    # the same place.
    print("FIXES:", fixes)
    anchor_info = BaseSegment.compute_anchor_edit_info(fixes)
    fixed_tree, _, _ = root.apply_fixes(
        default_config.get("dialect_obj"), "TEST", anchor_info
    )
    assert fixed_tree.raw == raw_sql_out, "Element check passed - but fix check failed!"
