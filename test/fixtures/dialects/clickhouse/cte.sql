with (
    select 1 as p
) as test_param

select
    toString(1) as Test_string,
    toDateTime64('2022-05-25', 3) as Test_dateTime64,
    ifNull(null, 'TestNull') as testIf,
    JSONExtractString('{"abc": "hello"}', 'abc') as testJSON,
    test_param as param;

WITH '2019-08-01 15:23:00' as ts_upper_bound
SELECT *
FROM hits
WHERE
    EventDate = toDate(ts_upper_bound) AND
    EventTime <= ts_upper_bound;

WITH sum(bytes) as s
SELECT
    formatReadableSize(s),
    table
FROM system.parts
GROUP BY table
ORDER BY s;

/* this example would return TOP 10 of most huge tables */
WITH
    (
        SELECT sum(bytes)
        FROM system.parts
        WHERE active
    ) AS total_disk_usage
SELECT
    (sum(bytes) / total_disk_usage) * 100 AS table_disk_usage,
    table
FROM system.parts
GROUP BY table
ORDER BY table_disk_usage DESC
LIMIT 10;

WITH test1 AS (SELECT i + 1, j + 1 FROM test1)
SELECT * FROM test1;
