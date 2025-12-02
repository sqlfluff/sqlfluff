-- query table in the metastore
SELECT
    a,
    b
FROM default.people10m;

-- query table by path
SELECT
    a,
    b
FROM DELTA.`/delta/people10m`;

-- query old snapshot by timestamp
SELECT
    a,
    b
FROM default.people10m@20190101000000000;

SELECT count(*)
FROM DELTA.`/delta/people10m@20190101000000000`;

SELECT count(*)
FROM DELTA.`/delta/people10m`
    TIMESTAMP AS OF "2019-01-01";

SELECT count(*)
FROM default.people10m
    TIMESTAMP AS OF "2019-01-01";

SELECT count(*)
FROM default.people10m
    TIMESTAMP AS OF date_sub(current_date(), 1);

SELECT count(*)
FROM default.people10m
    TIMESTAMP AS OF "2019-01-01 01:30:00.000";

-- query old snapshot by version
SELECT
    a,
    b
FROM default.people10m@v123;

SELECT count(*)
FROM default.people10m
    VERSION AS OF 5238;

SELECT count(*)
FROM default.people10m@v5238;

SELECT count(*)
FROM DELTA.`/delta/people10m@v5238`;

SELECT count(*)
FROM DELTA.`/delta/people10m`
    VERSION AS OF 5238;
