CREATE TABLE newtable (
    x INT64,
    y INT64
)
PARTITION BY y
AS
SELECT
    x,
    y
FROM
    table1
