CREATE TABLE newtable (
    x INT64,
    y INT64
)
PARTITION BY y
CLUSTER BY x, y
AS
SELECT
    x,
    y
FROM
    table1
