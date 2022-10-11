"""Tests for reindenting methods.

Specifically:
- ReflowPoint.indent_to()
- ReflowPoint.get_indent()
- deduce_line_indent()
"""

import logging
import pytest

from sqlfluff.core import Linter
from sqlfluff.utils.reflow.elements import ReflowBlock

from sqlfluff.utils.reflow.sequence import ReflowSequence
from sqlfluff.utils.reflow.reindent import (
    deduce_line_indent,
    map_reindent_lines,
    _ReindentLine,
    lint_reindent_lines,
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
    "raw_sql_in,lines",
    [
        # Trivial
        (
            "select 1",
            [
                _ReindentLine(0, 3, 0, ""),
            ],
        ),
        # Trivial with trailing newline
        (
            "select 1\n",
            [
                _ReindentLine(0, 3, 0, ""),
            ],
        ),
        # Trivial with leading newline
        (
            "\nselect 1",
            [
                _ReindentLine(0, 4, 0, ""),
            ],
        ),
        # Trivial with leading and trailing newline
        (
            "\nselect 1\n",
            [
                _ReindentLine(0, 4, 0, ""),
            ],
        ),
        # Simple without trailing newline
        (
            "select\n  1",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
            ],
        ),
        # Simple with trailing newline
        (
            "select\n  1\n",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
            ],
        ),
        # Example with an _untaken_ indents.
        # It's a little contrived but should illustrate the point.
        (
            "select (\n3)\n",
            [
                _ReindentLine(0, 3, 0, ""),
                _ReindentLine(3, 7, 2, "", untaken_indents=(1,)),
            ],
        ),
        (
            "select (((\n((\n3\n))\n)))",
            [
                _ReindentLine(0, 7, 0, ""),
                _ReindentLine(7, 11, 4, "", untaken_indents=(1, 2, 3)),
                _ReindentLine(11, 13, 6, "", untaken_indents=(1, 2, 3, 5)),
                _ReindentLine(13, 17, 5, "", untaken_indents=(1, 2, 3, 5)),
                _ReindentLine(17, 23, 3, "", untaken_indents=(1, 2, 3)),
            ],
        ),
        # More complex examples including templating.
        (
            "select\n  1\n  {% if false %}\n    + 2\n  {% endif %}",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
                _ReindentLine(3, 5, 0, "  ", True),
            ],
        ),
        (
            "select\n  1\n  {% if true %}\n    + 2\n  {% endif %}",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
                _ReindentLine(3, 5, 1, "  ", True),
                _ReindentLine(5, 9, 2, "    "),
                # NOTE: This indent balance is 1 not 0 despite the placement
                # of the dedent segment. This is because we "hoist" the closing
                # tag to match the opening one where possible.
                _ReindentLine(9, 11, 1, "  ", True),
            ],
        ),
        (
            "select\n  1\n  {% if true %}\n    , 2\n  FROM a\n{% endif %}",
            [
                # NOTE: Here because we can't hoist "up" we pull the opening
                # tag down to match the closing indent balance.
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
                _ReindentLine(3, 5, 0, "  ", True),  # Here's the sunken element.
                # These next two lines aren't further indented either.
                _ReindentLine(5, 9, 1, "    "),
                _ReindentLine(9, 13, 0, "  "),
                # The final tag then sits on the baseline.
                _ReindentLine(13, 15, 0, "", True),
            ],
        ),
        (
            "select\n  0,\n  {% for i in [1, 2, 3] %}\n    i,\n  {% endfor %}\n  4",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 5, 1, "  "),
                _ReindentLine(5, 7, 1, "  ", True),
                _ReindentLine(7, 11, 2, "    "),
                _ReindentLine(11, 13, 1, "  ", True),  # Loop Marker
                _ReindentLine(13, 17, 2, "    "),
                _ReindentLine(17, 19, 1, "  ", True),  # Loop Marker
                _ReindentLine(19, 23, 2, "    "),
                _ReindentLine(23, 25, 1, "  ", True),
                _ReindentLine(25, 27, 1, "  "),
            ],
        ),
        # Test that we don't get them for empty lines.
        (
            "\n\n  \n\nselect\n\n\n\n  \n\n     1\n\n  \n\n",
            [
                # Only two lines here
                _ReindentLine(0, 2, 0, ""),
                _ReindentLine(2, 4, 1, "     "),
            ],
        ),
    ],
)
def test_reflow__map_reindent_lines(raw_sql_in, lines, default_config, caplog):
    """Test the map_reindent_lines() method directly."""
    # Run the lexer at debug level here, so we can see
    # creation of indents and dedents.
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.lexer"):
        root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    # Logging to assist debugging
    for idx, elem in enumerate(seq.elements):
        if isinstance(elem, ReflowBlock) and "placeholder" in elem.class_types:
            print(idx, repr(elem.segments[0].source_str))
        else:
            print(idx, repr(elem.raw))
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules"):
        assert map_reindent_lines(seq.elements) == lines


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
        # ### Templated Multiline Cases ###
        # NOTE: the templated tags won't show here, but they
        # should still be indented.
        # Trailing tag
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
    ],
)
def test_reflow__lint_reindent_lines(raw_sql_in, raw_sql_out, default_config, caplog):
    """Test the lint_reindent_lines() method indirectly.

    Rather than testing directly, for brevity we check
    the raw output it produces. This results in a more
    compact test.
    """
    root = parse_ansi_string(raw_sql_in, default_config)
    print(root.stringify())
    seq = ReflowSequence.from_root(root, config=default_config)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        lines = map_reindent_lines(seq.elements)
        for idx, line in enumerate(lines):
            print(idx, line)
        # We're not testing the fixes directly at this stage.
        result, _ = lint_reindent_lines(
            seq.elements, lines, indent_unit="space", tab_space_size=2
        )

    result_raw = "".join(elem.raw for elem in result)
    assert result_raw == raw_sql_out
