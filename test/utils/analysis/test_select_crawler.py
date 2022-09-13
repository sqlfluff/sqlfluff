"""Test the select_crawler module."""
import pytest

from sqlfluff.core.linter.linter import Linter
from sqlfluff.utils.analysis import select_crawler


@pytest.mark.parametrize(
    "sql, expected_json",
    [
        (
            # Test trivial query.
            "select 1",
            {"selectables": ["select 1"]},
        ),
        (
            # Test set expression.
            "select 1 union select 2",
            {"selectables": ["select 1", "select 2"]},
        ),
        (
            # Test multiple CTEs.
            "with cte1 as (select 1 as x), cte2 as (select 2 as y) "
            "select * from cte1 join cte2 using (x)",
            {
                "ctes": {
                    "CTE1": {"selectables": ["select 1 as x"]},
                    "CTE2": {"selectables": ["select 2 as y"]},
                },
                "query_type": "WithCompound",
                "selectables": ["select * from cte1 join cte2 using (x)"],
            },
        ),
        (
            # Nested CTEs (from L044 test suite)
            """
        with a as (
            with b as (select 1 from c)
            select * from b
        )
        select * from a
        """,
            {
                "ctes": {
                    "A": {
                        "ctes": {"B": {"selectables": ["select 1 from c"]}},
                        "query_type": "WithCompound",
                        "selectables": ["select * from b"],
                    }
                },
                "query_type": "WithCompound",
                "selectables": ["select * from a"],
            },
        ),
        (
            # Nested CTEs (from L044 test suite)
            """
        with b as (select 1 from c)
        select * from (
            with a as (select * from b)
            select * from a
        )
        """,
            {
                "ctes": {"B": {"selectables": ["select 1 from c"]}},
                "query_type": "WithCompound",
                "selectables": [
                    "select * from (\n"
                    "            with a as (select * from b)\n"
                    "            select * from a\n"
                    "        )"
                ],
            },
        ),
        (
            # Test that subquery in "from" not included.
            "select a.x from (select z from b)",
            {"selectables": ["select a.x from (select z from b)"]},
        ),
        (
            # Test that subquery in "from" / "join" not included.
            "select a.x from a join (select z from b) as b on (a.x = b.x)",
            {
                "selectables": [
                    "select a.x from a join (select z from b) as b on (a.x = b.x)"
                ]
            },
        ),
        (
            # In CTE main query, test that subquery in "from" not included.
            "with prep as (select 1) select a.x from (select z from b)",
            {
                "ctes": {"PREP": {"selectables": ["select 1"]}},
                "query_type": "WithCompound",
                "selectables": ["select a.x from (select z from b)"],
            },
        ),
        (
            # In CTE main query, test that subquery in "from" / "join" not included.
            "with prep as (select 1) "
            "select a.x from a join (select z from b) as b on (a.x = b.x)",
            {
                "ctes": {"PREP": {"selectables": ["select 1"]}},
                "query_type": "WithCompound",
                "selectables": [
                    "select a.x from a join (select z from b) as b on (a.x = " "b.x)"
                ],
            },
        ),
        (
            """with prep_1 as (
    with d as (
        select x, z from b
    )
    select * from d
)
select
    a.x, a.y, b.z
from a
join prep_1 using (x)
""",
            {
                "ctes": {
                    "PREP_1": {
                        "ctes": {
                            "D": {"selectables": ["select x, z from b"]},
                        },
                        "query_type": "WithCompound",
                        "selectables": ["select * from d"],
                    }
                },
                "query_type": "WithCompound",
                "selectables": [
                    "select\n    a.x, a.y, b.z\nfrom a\njoin prep_1 using (x)"
                ],
            },
        ),
    ],
)
def test_select_crawler_constructor(sql, expected_json):
    """Test SelectCrawler when created using constructor."""
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql)
    segments = list(
        parsed.tree.recursive_crawl(
            "with_compound_statement",
            "set_expression",
            "select_statement",
        )
    )
    segment = segments[0]
    crawler = select_crawler.SelectCrawler(segment, linter.dialect)
    assert all(
        cte.cte_definition_segment is not None
        for cte in crawler.query_tree.ctes.values()
    )
    json_query_tree = crawler.query_tree.as_json()
    assert expected_json == json_query_tree


def test_select_crawler_nested():
    """Test invoking with an outer from_expression_segment."""
    sql = """
select
    a.x, a.y, b.z
from a
join (
    with d as (
        select x, z from b
    )
    select * from d
) using (x)
    """
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql)
    segments = list(
        parsed.tree.recursive_crawl(
            "with_compound_statement",
            "set_expression",
            "select_statement",
        )
    )
    segment = segments[0]
    crawler = select_crawler.SelectCrawler(segment, linter.dialect)
    sc = select_crawler.SelectCrawler(
        crawler.query_tree.selectables[0]
        .select_info.table_aliases[1]
        .from_expression_element,
        linter.dialect,
    )
    assert sc.query_tree.as_json() == {
        "selectables": [
            "select * from d",
        ],
        "ctes": {"D": {"selectables": ["select x, z from b"]}},
        "query_type": "WithCompound",
    }
