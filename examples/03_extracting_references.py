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
# Under the hood we look for all of the table references
# which aren't also CTE aliases.
external_tables = parsed.tree.get_table_references()
# external_tables == {'bar.bar', 'bap', 'ban'}
