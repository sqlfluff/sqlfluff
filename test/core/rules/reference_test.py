"""Test components for working with object and table references."""

import pytest

from sqlfluff.core.rules import reference


@pytest.mark.parametrize(
    "possible_references, targets, result",
    [
        # Empty list of references is always True.
        [[], [("abc",)], True],
        # Simple cases: one reference, one target.
        [[("agent1",)], [("agent1",)], True],
        [[("agent1",)], [("customer",)], False],
        # Multiple references. If any match, good.
        [[("bar",), ("user_id",)], [("bar",)], True],
        [[("foo",), ("user_id",)], [("bar",)], False],
        # Multiple targets. If any reference matches, good.
        [[("table1",)], [("table1",), ("table2",), ("table3",)], True],
        [[("tbl2",)], [("db", "sc", "tbl1")], False],
        [[("tbl2",)], [("db", "sc", "tbl2")], True],
        # Multi-part references and targets. If one tuple is shorter than
        # the other, checks for a suffix match.
        [
            [
                (
                    "rc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            False,
        ],
        [
            [
                (
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            True,
        ],
        [
            [
                (
                    "cb",
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            False,
        ],
        [
            [
                (
                    "db",
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            True,
        ],
        [[("public", "agent1")], [("agent1",)], True],
        [[("public", "agent1")], [("public",)], False],
    ],
)
def test_object_ref_matches_table(possible_references, targets, result):
    """Test object_ref_matches_table()."""
    assert reference.object_ref_matches_table(possible_references, targets) == result
