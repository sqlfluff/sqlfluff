-- Block comments containing bracket characters (e.g. `min(` and `)`) must not be
-- treated as real brackets by the parser's bracket-matching optimisation.
-- See https://github.com/sqlfluff/sqlfluff/issues/7914
CREATE TABLE table_b
AS (
  SELECT
      col_a
      /*
      min(
      )
      AS type_arr
      */
  FROM table_a
)
