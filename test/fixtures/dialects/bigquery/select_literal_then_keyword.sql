-- Issue 9096: `|>` among BigQuery's select terminators lifts the
-- whitespace-before-keyword rule, so FROM ends the clause here.
SELECT 'a'FROM t;

SELECT 1 AS x, "b"FROM t;
