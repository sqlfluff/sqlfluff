"""This is an example of how to extract table names."""

import sqlfluff

query_with_ctes = """
WITH foo AS (SELECT * FROM bar.bar),
baz AS (SELECT * FROM bap)
SELECT * FROM foo
INNER JOIN baz USING (user_id)
INNER JOIN ban USING (user_id)
"""

#  -------- PARSING ----------
parsed = sqlfluff.parse(query_with_ctes)

#  -------- EXTRACTION ----------
# Note that this is still outline functionality and this
# logic may eventually be brough into more convenient
# helper methods. For now the recommendation is for
# libraries to use the low level abstractions to extract
# elements they need for their own purposes.
tbl_refs = set(tbl_ref.raw for tbl_ref in parsed.tree.recursive_crawl("table_reference"))
# tbl_refs == {'bap', 'ban', 'baz', 'foo', 'bar.bar'}
cte_refs = set(cte_def.get_identifier().raw for cte_def in parsed.tree.recursive_crawl("common_table_expression"))
# cte_refs == {'baz', 'foo'}
external_tables = tbl_refs - cte_refs
# external_tables == {'bar.bar', 'bap', 'ban'}
