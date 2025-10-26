"""Tests for reindenting methods.

Specifically:
- ReflowPoint.indent_to()
- ReflowPoint.get_indent()
- deduce_line_indent()
"""

import logging
import sys
from typing import Callable

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter.fix import apply_fixes, compute_anchor_edit_info
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.plugin.host import get_plugin_manager, purge_plugin_manager
from sqlfluff.core.templaters import RawTemplater
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice
from sqlfluff.core.templaters.jinja import JinjaTemplater
from sqlfluff.utils.reflow.helpers import deduce_line_indent, fixes_from_results
from sqlfluff.utils.reflow.reindent import (
    _crawl_indent_points,
    _IndentLine,
    _IndentPoint,
    lint_indent_points,
)
from sqlfluff.utils.reflow.sequence import ReflowSequence


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).tree


class SpecialMarkerInserter(JinjaTemplater):
    """Inserts special marker slices in a sliced file.

    Some templater plugins might insert custom marker slices that are of zero source
    string length, including an empty source string.  This mock templater simulates
    this behavior by adding a marker slice like this after every block_start slice.
    """

    name = "special_marker_inserter"

    def slice_file(
        self, raw_str: str, render_func: Callable[[str], str], config=None
    ) -> tuple[list[RawFileSlice], list[TemplatedFileSlice], str]:
        """Patch a sliced file returned by the superclass."""
        raw_sliced, sliced_file, templated_str = super().slice_file(
            raw_str, render_func, config
        )

        patched_sliced_file = []
        for templated_slice in sliced_file:
            patched_sliced_file.append(templated_slice)
            # Add an EMPTY special_marker slice after every block_start.
            if templated_slice.slice_type == "block_start":
                # Note that both the source_slice AND the templated_slice are empty.
                source_pos = templated_slice.source_slice.stop
                templated_pos = templated_slice.templated_slice.stop
                patched_sliced_file.append(
                    TemplatedFileSlice(
                        "special_marker",
                        slice(source_pos, source_pos),
                        slice(templated_pos, templated_pos),
                    )
                )

        return raw_sliced, patched_sliced_file, templated_str


@hookimpl
def get_templaters() -> list[type[RawTemplater]]:
    """Return templaters provided by this test module."""
    return [SpecialMarkerInserter]


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
    "raw_sql_in,templater,points_out",
    [
        # Trivial
        (
            "select 1",
            "raw",
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
            "raw",
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
            "raw",
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
            "raw",
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
                # an indent here. We *SHOULDN'T* have an untaken indent here,
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
            "raw",
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
        # Trailing comment case: delays indent until after the comment
        (
            "SELECT -- comment\n    1;",
            "raw",
            [
                # No point at the start.
                # After SELECT
                _IndentPoint(1, 0, 0, 0, None, False, ()),
                # After comment
                _IndentPoint(3, 1, 0, 0, None, True, ()),
                # After 1
                _IndentPoint(5, -1, -1, 1, 3, False, ()),
                # After ;
                _IndentPoint(7, 0, 0, 0, 3, False, ()),
            ],
        ),
        # Two trailing comments
        (
            "SELECT /* first comment */ /* second comment */\n    1;",
            "raw",
            [
                # No point at the start.
                # After SELECT
                _IndentPoint(1, 0, 0, 0, None, False, ()),
                # After first comment
                _IndentPoint(3, 0, 0, 0, None, False, ()),
                # After second comment
                _IndentPoint(5, 1, 0, 0, None, True, ()),
                # After 1
                _IndentPoint(7, -1, -1, 1, 5, False, ()),
                # After ;
                _IndentPoint(9, 0, 0, 0, 5, False, ()),
            ],
        ),
        # Templated case
        (
            "SELECT\n"
            "    {{ 'a' }}\n"
            "    {% for c in ['d', 'e'] %}\n"
            "    ,{{ c }}_val\n"
            "    {% endfor %}\n",
            "jinja",
            [
                # No initial indent (this is the first newline).
                _IndentPoint(1, 1, 0, 0, None, True, ()),
                # point after a
                _IndentPoint(3, 0, 0, 1, 1, True, ()),
                # point after for
                _IndentPoint(5, 1, 0, 1, 3, True, ()),
                # point after d_val
                _IndentPoint(9, -1, -1, 2, 5, True, ()),
                # point after loop
                _IndentPoint(11, 1, 0, 1, 9, True, ()),
                # point after e_val
                _IndentPoint(15, -2, -2, 2, 11, True, ()),
                # point after endfor
                _IndentPoint(17, 0, 0, 0, 15, True, ()),
            ],
        ),
        # Templated case (with consuming whitespace)
        (
            "{% for item in [1, 2] -%}\n"
            "SELECT *\n"
            "FROM some_table\n"
            "{{ 'UNION ALL\n' if not loop.last }}\n"
            "{%- endfor %}",
            "jinja",
            [
                # No initial indent (this is the first newline).
                # Importantly this first point - IS a newline
                # even though that newline segment is consumed
                # it should still be True here.
                _IndentPoint(1, 1, 0, 0, None, True, ()),
                # point between SELECT & *
                _IndentPoint(3, 1, 0, 1, 1, False, ()),
                # point after *
                _IndentPoint(5, -1, -1, 2, 1, True, (2,)),
                # point after FROM
                _IndentPoint(7, 1, 0, 1, 5, False, ()),
                # point after some_table
                _IndentPoint(9, -1, -1, 2, 5, True, (2,)),
                # point after ALL (we dedent down to the loop marker).
                _IndentPoint(13, -1, -1, 1, 9, True, ()),
                # There should be a loop marker here.
                # point after loop marker and before SELECT
                # (we indent back up after the loop).
                _IndentPoint(15, 1, 0, 0, 13, True, ()),
                # point between SELECT & *
                _IndentPoint(17, 1, 0, 1, 15, False, ()),
                # point after *
                _IndentPoint(19, -1, -1, 2, 15, True, (2,)),
                # point after FROM
                _IndentPoint(21, 1, 0, 1, 19, False, ()),
                # point after some_table (and before unused placeholder)
                _IndentPoint(23, -1, -1, 2, 19, True, (2,)),
                # Point after placeholder and dedenting down to endfor
                _IndentPoint(25, -1, -1, 1, 23, True, ()),
                # Point between endfor and end-of-file
                _IndentPoint(27, 0, 0, 0, 25, False, ()),
            ],
        ),
        # Templated case (with templated newline and indent)
        (
            "SELECT\n  {{'1 \n, 2'}}\nFROM foo",
            "jinja",
            [
                # After SELECT
                _IndentPoint(1, 1, 0, 0, None, True, ()),
                # NOTE: The newline inside the tag isn't reported.
                # After the templated section (hence why 7)
                _IndentPoint(7, -1, -1, 1, 1, True, ()),
                # After FROM
                _IndentPoint(9, 1, 0, 0, 7, False, ()),
                # After foo
                _IndentPoint(11, -1, -1, 1, 7, False, (1,)),
            ],
        ),
        # Templated case (with special marker slice that has no source string)
        (
            # The invisible special marker slice will be inserted immediately after
            # the first normal template section.
            "{% if True %}\n    SELECT 1;\n{% endif %}\n",
            "special_marker_inserter",
            [
                # No point at the start.
                # After the {% if True %} block: this should not yet indent because
                # there's still the upcoming zero-length special_marker
                # TemplateSegment.  This is handled similar to the trailing comment
                # test case.
                _IndentPoint(1, 0, 0, 0, None, False, ()),
                # After the zero-length special_marker TemplateSegment inserted by
                # the special templater: only after this do we want to indent.
                _IndentPoint(3, 1, 0, 0, None, True, ()),
                # After SELECT
                _IndentPoint(5, 1, 0, 1, 3, False, ()),
                # After 1
                _IndentPoint(7, -1, -1, 2, 3, False, (2,)),
                # After ;
                _IndentPoint(9, -1, -1, 1, 3, True, ()),
                # After {% endif %}
                _IndentPoint(11, 0, 0, 0, 9, True, ()),
            ],
        ),
    ],
)
def test_reflow__crawl_indent_points(raw_sql_in, templater, points_out, caplog):
    """Test _crawl_indent_points directly."""
    # Register the mock templater in this module.
    purge_plugin_manager()
    get_plugin_manager().register(sys.modules[__name__], name="reindent_test")

    config = FluffConfig(overrides={"dialect": "ansi", "templater": templater})
    root = parse_ansi_string(raw_sql_in, config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=config)
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
        # Templated cases.
        # NOTE: We're just rendering the fixed file in the templated space
        # so that for these tests we don't touch the fix routines. That's
        # why the template tags aren't visible - BUT THEIR INDENTS SHOULD BE.
        # This one is useful for ensuring the tags have the same indent.
        # ... first with a FROM
        (
            "SELECT\n"
            "    {{ 'a' }}\n"
            "    {% for c in ['d', 'e'] %}\n"
            "    ,{{ c }}_val\n"
            "    {% endfor %}\n"
            "FROM foo",
            "SELECT\n  a\n  \n    ,d_val\n  \n    ,e_val\n  \nFROM foo",
        ),
        # ... then without a FROM
        (
            "SELECT\n"
            "    {{ 'a' }}\n"
            "    {% for c in ['d', 'e'] %}\n"
            "    ,{{ c }}_val\n"
            "    {% endfor %}\n",
            "SELECT\n  a\n  \n    ,d_val\n  \n    ,e_val\n  \n",
        ),
        # This one is useful for if statements get handled right.
        # NOTE: There's a template loop in the middle.
        (
            "SELECT\n"
            "  {{ 'a' }}\n"
            "  {% for c in ['d', 'e'] %}\n"
            " {% if c == 'd' %}\n"
            "  ,{{ c }}_val_a\n"
            "    {% else %}\n"
            "  ,{{ c }}_val_b\n"
            "{% endif %}\n"
            "  {% endfor %}\n",
            "SELECT\n"
            "  a\n"
            "  \n"
            "    \n"
            "      ,d_val_a\n"
            "    \n"
            "  \n"
            "    \n"
            "      ,e_val_b\n"
            "    \n"
            "  \n",
        ),
        # Test leading templated newlines.
        # https://github.com/sqlfluff/sqlfluff/issues/4485
        (
            "{{ '\\n   \\n   ' }}\nSELECT 1",
            # NOTE: This looks a little strange, but what's important
            # here is that it doesn't raise an exception.
            "\n   \n   \nSELECT 1",
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
        elements, results = lint_indent_points(seq.elements, single_indent="  ")

    result_raw = "".join(elem.raw for elem in elements)
    assert result_raw == raw_sql_out, "Raw Element Check Failed!"

    # Now we've checked the elements - check that applying the fixes gets us to
    # the same place.
    print("Results:", results)
    anchor_info = compute_anchor_edit_info(fixes_from_results(results))
    fixed_tree, _, _, valid = apply_fixes(
        root, default_config.get("dialect_obj"), "TEST", anchor_info
    )
    assert valid, f"Reparse check failed: {fixed_tree.raw!r}"
    assert fixed_tree.raw == raw_sql_out, "Element check passed - but fix check failed!"


@pytest.mark.parametrize(
    "indent_line, forced_indents, expected_units",
    [
        # Trivial case of a first line.
        (
            _IndentLine(0, [_IndentPoint(0, 0, 0, 0, None, False, ())]),
            [],
            0,
        ),
        # Simple cases of a normal lines.
        (
            _IndentLine(3, [_IndentPoint(6, 0, 0, 3, 1, True, ())]),
            [],
            3,
        ),
        (
            # NOTE: Initial indent for *line* is different to *point*.
            # The *line* takes precedence.
            _IndentLine(1, [_IndentPoint(6, 0, 0, 3, 1, True, ())]),
            [],
            1,
        ),
        # Indents and dedents on the line break.
        # NOTE: The line indent still takes precedence here.
        (
            _IndentLine(3, [_IndentPoint(6, 1, 0, 3, 1, True, ())]),
            [],
            3,
        ),
        (
            _IndentLine(3, [_IndentPoint(6, -1, -1, 3, 1, True, ())]),
            [],
            3,
        ),
        # Handle untaken indents.
        (
            _IndentLine(3, [_IndentPoint(6, 0, 0, 3, 1, True, (1,))]),
            [],
            2,
        ),
        (
            _IndentLine(3, [_IndentPoint(6, 0, 0, 3, 1, True, (1, 2))]),
            [],
            1,
        ),
        (
            _IndentLine(3, [_IndentPoint(6, 0, 0, 3, 1, True, (2,))]),
            # Forced indent takes us back up.
            [2],
            3,
        ),
        (
            _IndentLine(3, [_IndentPoint(6, 0, 0, 3, 1, True, (3,))]),
            [],
            2,
        ),
        (
            _IndentLine(3, [_IndentPoint(6, 0, -1, 3, 1, True, (3,))]),
            # Untaken indent is pruned by trough.
            [],
            3,
        ),
    ],
)
def test_reflow__desired_indent_units(indent_line, forced_indents, expected_units):
    """Test _IndentLine.desired_indent_units() directly."""
    assert indent_line.desired_indent_units(forced_indents) == expected_units


@pytest.mark.parametrize(
    "spacing_after_value,should_raise",
    [
        ("single", False),
        ("touch", False),
        ("any", True),
        ("touch:inline", True),
        ("align", True),
        ("unsupported_value", True),
    ],
)
def test_reflow__reindent_spacing_after_with_align_following(
    spacing_after_value, should_raise, default_config
):
    """Test spacing_after values with line_position="leading:align-following".

    This tests both valid ("single", "touch") and unsupported spacing_after
    values when line_position is set to "leading:align-following". Unsupported
    values should raise NotImplementedError.
    """
    from sqlfluff.utils.reflow.config import ReflowConfig

    # Create SQL that includes a comma
    raw_sql = "select\n  1,\n  2"

    # Parse the SQL first
    root = parse_ansi_string(raw_sql, default_config)

    # Create a custom reflow config with the specific settings
    custom_config_dict = {
        "comma": {
            "line_position": "leading:align-following",
            "spacing_after": spacing_after_value,
        }
    }
    reflow_config = ReflowConfig.from_dict(
        custom_config_dict,
        indent_unit="space",
        tab_space_size=4,
    )

    # Create a reflow sequence with the custom config
    seq = ReflowSequence.from_root(root, config=default_config)
    # Override the reflow_config with our custom one
    seq = ReflowSequence(
        elements=seq.elements,
        root_segment=seq.root_segment,
        reflow_config=reflow_config,
        depth_map=seq.depth_map,
    )

    if should_raise:
        # This should raise NotImplementedError
        with pytest.raises(
            NotImplementedError,
            match=r"spacing after type of `.+` is not supported",
        ):
            seq.reindent()
    else:
        # This should succeed without raising an exception
        result = seq.reindent()
        assert result is not None


def test_reflow__indent_compensation_insufficient_space_warning(default_config, caplog):
    """Test warning when there's insufficient space for indent compensation.

    This tests the code path in _calculate_desired_starting_indent where
    there isn't enough indentation space to compensate for leading comma/operator
    alignment, triggering the warning at reindent.py:1355-1360.
    """
    from sqlfluff.utils.reflow.config import ReflowConfig

    # Create SQL with a binary operator on a line that needs minimal indent
    # Using "AND" (3 chars) + spacing_after (1 space) = 4 chars compensation
    # But the line only has 1 indent unit = 2 spaces with tab_space_size=2
    # This triggers: len("  ") < abs(-4) → 2 < 4 → True
    raw_sql = "select 1\nwhere true\nAND false"

    # Parse the SQL first
    root = parse_ansi_string(raw_sql, default_config)

    # Create a custom reflow config with:
    # - tab_space_size=2 (small indent)
    # - binary_operator with line_position="leading:align-following"
    # - spacing_after="single" (adds 1 space to compensation)
    custom_config_dict = {
        "binary_operator": {
            "line_position": "leading:align-following",
            "spacing_after": "single",
        }
    }
    reflow_config = ReflowConfig.from_dict(
        custom_config_dict,
        indent_unit="space",
        tab_space_size=2,  # Small indent to trigger insufficient space
    )

    # Create a reflow sequence with the custom config
    seq = ReflowSequence.from_root(root, config=default_config)
    seq = ReflowSequence(
        elements=seq.elements,
        root_segment=seq.root_segment,
        reflow_config=reflow_config,
        depth_map=seq.depth_map,
    )

    # Call reindent and check for the warning
    with caplog.at_level(logging.WARNING, logger="sqlfluff.utils.reflow"):
        result = seq.reindent()
        assert result is not None

    # Verify the warning was logged
    assert any(
        "Not enough space to compensate indentation" in record.message
        and "Ignoring indentation compensation" in record.message
        for record in caplog.records
    ), "Expected warning about insufficient indentation space was not logged"


def test_reflow__indent_compensation_success_path(default_config, caplog):
    """Test successful indent compensation for leading comma/operator alignment.

    This tests the code path in _calculate_desired_starting_indent where
    there IS enough indentation space to compensate, triggering the debug
    log and successful compensation at reindent.py:1363-1367.
    """
    from sqlfluff.utils.reflow.config import ReflowConfig

    # Create SQL with a comma on subsequent lines
    # Using comma + spacing_after will require compensation
    raw_sql = "select\n    1\n    , 2\n    , 3"

    # Parse the SQL first
    root = parse_ansi_string(raw_sql, default_config)

    # Create a custom reflow config with:
    # - comma with line_position="leading:align-following"
    # - spacing_after="single" (adds 1 space after comma)
    # - tab_space_size=4 (enough space for compensation)
    custom_config_dict = {
        "comma": {
            "line_position": "leading:align-following",
            "spacing_after": "single",
        }
    }
    reflow_config = ReflowConfig.from_dict(
        custom_config_dict,
        indent_unit="space",
        tab_space_size=4,  # Large enough indent for compensation
    )

    # Create a reflow sequence with the custom config
    seq = ReflowSequence.from_root(root, config=default_config)
    seq = ReflowSequence(
        elements=seq.elements,
        root_segment=seq.root_segment,
        reflow_config=reflow_config,
        depth_map=seq.depth_map,
    )

    # Call reindent and check for the debug log
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = seq.reindent()
        assert result is not None

    # Verify the compensation debug log was recorded
    assert any(
        "Compensating the starting indent by" in record.message
        for record in caplog.records
    ), "Expected debug log about indentation compensation was not logged"
