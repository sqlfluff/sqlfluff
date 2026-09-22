-- SQL pipeline. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-pipeline
FROM t |> SELECT a;

FROM t |> WHERE a > 1;

TABLE t |> SELECT a;

-- A pipeline may have zero operations: the query is valid on its own.
FROM t;
