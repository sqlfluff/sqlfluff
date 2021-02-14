"""Test using sqlfluff to extract elements of queries."""

import pytest

import sqlfluff

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

query_with_ctes = """
WITH foo AS (SELECT * FROM bar.bar),
baz AS (SELECT * FROM bap)
SELECT * FROM foo
INNER JOIN baz USING (user_id)
INNER JOIN ban USING (user_id)
"""


@pytest.mark.parametrize(
    "sql,table_refs",
    [
        (my_bad_query, {"myTable"}),
        (query_with_ctes, {"bar.bar", "bap", "ban"}),
    ],
)
def test__api__util_get_table_references(sql, table_refs):
    """Basic checking of lint functionality."""
    parsed = sqlfluff.parse(sql)
    external_tables = parsed.tree.get_table_references()
    assert external_tables == table_refs
