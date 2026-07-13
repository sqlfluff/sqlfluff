"""Tests specific to the ClickHouse dialect."""

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
