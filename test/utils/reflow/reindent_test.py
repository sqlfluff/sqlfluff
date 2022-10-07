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
        # More complex examples including templating.
        (
            "select\n  1\n  {% if false %}\n    + 2\n  {% endif %}",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
                _ReindentLine(3, 5, 0, "  "),
            ],
        ),
        (
            "select\n  1\n  {% if true %}\n    + 2\n  {% endif %}",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 3, 1, "  "),
                _ReindentLine(3, 5, 1, "  "),
                _ReindentLine(5, 9, 2, "    "),
                _ReindentLine(9, 11, 0, "  "),
            ],
        ),
        (
            "select\n  0,\n  {% for i in [1, 2, 3] %}\n    i,\n  {% endfor %}\n  4",
            [
                _ReindentLine(0, 1, 0, ""),
                _ReindentLine(1, 5, 1, "  "),
                _ReindentLine(5, 7, 1, "  "),
                _ReindentLine(7, 11, 2, "    "),
                _ReindentLine(11, 13, 1, "  "),
                _ReindentLine(13, 17, 2, "    "),
                _ReindentLine(17, 19, 1, "  "),
                _ReindentLine(19, 23, 2, "    "),
                _ReindentLine(23, 25, 1, "  "),
                _ReindentLine(25, 27, 1, "  "),
            ],
        ),
    ],
)
def test_reflow__map_reindent_lines(raw_sql_in, lines, default_config, caplog):
    """Test the deduce_line_indent() method directly."""
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
