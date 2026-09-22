-- MATCH_RECOGNIZE. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-match-recognize
SELECT * FROM t MATCH_RECOGNIZE (PATTERN (a) DEFINE a AS TRUE);

SELECT symbol
FROM stock
MATCH_RECOGNIZE (
    PARTITION BY symbol
    ORDER BY tstamp
    MEASURES FIRST(tstamp) AS s
    ONE ROW PER MATCH
    AFTER MATCH SKIP PAST LAST ROW
    PATTERN (strt up+)
    DEFINE up AS price > PREV(price)
) AS T;
