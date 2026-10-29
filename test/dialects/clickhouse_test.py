"""Tests specific to the ClickHouse dialect."""

import pytest

from sqlfluff.core import Linter


def test_group_by_modifiers_are_inside_indent() -> None:
    """Keep ClickHouse GROUP BY modifiers inside the clause indentation."""
    parsed = Linter(dialect="clickhouse").parse_string(
        "SELECT a, count() FROM t GROUP BY a WITH TOTALS HAVING count() > 1;"
    )

    assert parsed.tree is not None
    assert not parsed.violations
    groupby = next(parsed.tree.recursive_crawl("groupby_clause"))
    segment_types = [segment.type for segment in groupby.segments]
    totals_index = next(
        index
        for index, segment in enumerate(groupby.segments)
        if segment.raw_upper == "TOTALS"
    )

    assert segment_types.index("indent") < totals_index < segment_types.index("dedent")


@pytest.mark.parametrize(
    "sql",
    [
        "ALTER TABLE t ADD COLUMN a UInt8, ;",
        "ALTER TABLE t ADD COLUMN a UInt8,, ADD COLUMN b UInt8;",
        "ALTER TABLE t , ADD COLUMN a UInt8;",
    ],
)
def test_alter_table_rejects_malformed_action_lists(sql: str) -> None:
    """A comma must separate two complete ALTER TABLE actions."""
    parsed = Linter(dialect="clickhouse").parse_string(sql)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors
