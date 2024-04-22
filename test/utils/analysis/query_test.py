"""Test the select_crawler module."""

import pytest

from sqlfluff.core.linter.linter import Linter
from sqlfluff.utils.analysis.query import Query


def _parse_and_crawl_outer(sql):
    """Helper function for select crawlers.

    Given a SQL statement this crawls the SQL and instantiates
    a Query on the outer relevant segment.
    """
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql).root_variant()
    # Make sure it's fully parsable.
    assert "unparsable" not in parsed.tree.descendant_type_set
    # Create a crawler from the root segment.
    query = Query.from_root(parsed.tree, linter.dialect)
    # Analyse the segment.
    return query, linter


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
            # Nested CTEs (from AM04 test suite)
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
            # Nested CTEs (from AM04 test suite)
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
                "subqueries": [
                    # NOTE: Subquery from the FROM clause.
                    {
                        "ctes": {"A": {"selectables": ["select * from b"]}},
                        "query_type": "WithCompound",
                        "selectables": ["select * from a"],
                    },
                ],
            },
        ),
        (
            # Test that subquery in "from" not included.
            "select a.x from (select z from b)",
            {
                "selectables": ["select a.x from (select z from b)"],
                "subqueries": [{"selectables": ["select z from b"]}],
            },
        ),
        (
            # Test that subquery in "from" / "join" not included.
            "select a.x from a join (select z from b) as b on (a.x = b.x)",
            {
                "selectables": [
                    "select a.x from a join (select z from b) as b on (a.x = b.x)"
                ],
                "subqueries": [{"selectables": ["select z from b"]}],
            },
        ),
        (
            # In CTE main query, test that subquery in "from" not included.
            "with prep as (select 1) select a.x from (select z from b)",
            {
                "ctes": {"PREP": {"selectables": ["select 1"]}},
                "query_type": "WithCompound",
                "selectables": ["select a.x from (select z from b)"],
                "subqueries": [{"selectables": ["select z from b"]}],
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
                "subqueries": [{"selectables": ["select z from b"]}],
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
        # Test with a UNION as the main selectable of a WITH
        (
            "with a as (select 1), b as (select 2) "
            "select * from a union select * from b\n",
            {
                "ctes": {
                    "A": {"selectables": ["select 1"]},
                    "B": {"selectables": ["select 2"]},
                },
                "query_type": "WithCompound",
                "selectables": [
                    "select * from a",
                    "select * from b",
                ],
            },
        ),
        # Test with a VALUES clause in a WITH
        (
            "WITH txt AS ( VALUES (1, 'foo') ) SELECT * FROM txt\n",
            {
                "ctes": {
                    "TXT": {"selectables": ["VALUES (1, 'foo')"]},
                },
                "query_type": "WithCompound",
                "selectables": [
                    "SELECT * FROM txt",
                ],
            },
        ),
        # Test with Subqueries
        (
            "SELECT (\n"
            "    SELECT other_table.other_table_field_1 FROM other_table\n"
            "    WHERE other_table.id = field_2\n"
            ") FROM\n"
            "(SELECT * FROM some_table) AS my_alias\n",
            {
                "selectables": [
                    "SELECT (\n"
                    "    SELECT other_table.other_table_field_1 FROM other_table\n"
                    "    WHERE other_table.id = field_2\n"
                    ") FROM\n"
                    "(SELECT * FROM some_table) AS my_alias",
                ],
                "subqueries": [
                    {
                        "selectables": [
                            "SELECT other_table.other_table_field_1 FROM other_table\n"
                            "    WHERE other_table.id = field_2",
                        ]
                    },
                    {"selectables": ["SELECT * FROM some_table"]},
                ],
            },
        ),
        # Test a MERGE
        (
            """MERGE INTO t USING (SELECT * FROM u) AS u ON (a = b)
WHEN MATCHED THEN
UPDATE SET a = b
WHEN NOT MATCHED THEN
INSERT (b) VALUES (c);""",
            {
                "selectables": [
                    """MERGE INTO t USING (SELECT * FROM u) AS u ON (a = b)
WHEN MATCHED THEN
UPDATE SET a = b
WHEN NOT MATCHED THEN
INSERT (b) VALUES (c)"""  # NOTE: No trailing semicolon
                ],
                "subqueries": [{"selectables": ["SELECT * FROM u"]}],
            },
        ),
        # Test a DELETE
        (
            """DELETE FROM agent1
WHERE EXISTS(
    SELECT customer.cust_id FROM customer
    WHERE agent1.agent_code <> customer.agent_code);""",
            {
                "selectables": [
                    """SELECT customer.cust_id FROM customer
    WHERE agent1.agent_code <> customer.agent_code"""
                ]
            },
        ),
        # Test an UPDATE
        (
            """UPDATE my_table
SET row_sum = (
    SELECT COUNT(*) AS row_sum
    FROM
        another_table
    WHERE
        another_table.id = my_tableeee.id
)""",
            {
                "selectables": [
                    """SELECT COUNT(*) AS row_sum
    FROM
        another_table
    WHERE
        another_table.id = my_tableeee.id"""
                ]
            },
        ),
    ],
)
def test_select_crawler_constructor(sql, expected_json):
    """Test Query when created using constructor."""
    query, _ = _parse_and_crawl_outer(sql)
    assert all(cte.cte_definition_segment is not None for cte in query.ctes.values())
    query_dict = query.as_dict()
    assert expected_json == query_dict


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
    query, linter = _parse_and_crawl_outer(sql)

    inner_from = (
        query.selectables[0].select_info.table_aliases[1].from_expression_element
    )
    inner_select = next(inner_from.recursive_crawl("with_compound_statement"))
    inner_query = Query.from_segment(inner_select, linter.dialect)
    assert inner_query.as_dict() == {
        "selectables": [
            "select * from d",
        ],
        "ctes": {"D": {"selectables": ["select x, z from b"]}},
        "query_type": "WithCompound",
    }
