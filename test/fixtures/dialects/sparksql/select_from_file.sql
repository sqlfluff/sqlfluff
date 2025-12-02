-- PARQUET file
SELECT
    a,
    b,
    c
FROM PARQUET.`examples/src/main/resources/users.parquet`;

-- Directory of Parquet Files
SELECT
    a,
    b,
    c
FROM PARQUET.`examples/src/main/resources/users`;

-- ORC file
SELECT
    a,
    b,
    c
FROM ORC.`examples/src/main/resources/users.orc`;

-- JSON file
SELECT
    a,
    b,
    c
FROM JSON.`examples/src/main/resources/people.json`;

-- Directory of JSON files
SELECT
    a,
    b,
    c
FROM JSON.`examples/src/main/resources/people`;

-- Text File
SELECT
    a,
    b,
    c
FROM TEXT.`examples/src/main/resources/people.txt`;

-- Tests for Inline Path Glob Filter
-- https://spark.apache.org/docs/latest/sql-data-sources-generic-options.html#path-global-filter  --noqa: LT05
-- Inline Path Filter using Asterisk (*)
SELECT
    a,
    b,
    c
FROM TEXT.`//root/*.txt`;

-- Inline Path Filter using Question mark (?)
SELECT
    a,
    b,
    c
FROM TEXT.`//root/200?.txt`;

-- Inline Path Filter using Character Class ([ab])
SELECT
    a,
    b,
    c
FROM TEXT.`//root/200[23].txt`;

-- Inline Path Filter using Negated Character Class ([^ab])
SELECT
    a,
    b,
    c
FROM TEXT.`//root/200[^23].txt`;

-- Inline Path Filter using Character Range ([a-b])
SELECT
    a,
    b,
    c
FROM TEXT.`//root/200[2-5].txt`;

-- Inline Path Filter using Negated Character Range ([^a-b])
SELECT
    a,
    b,
    c
FROM TEXT.`//root/200[^2-5].txt`;

-- Inline Path Filter using Alternation ({a,b})
SELECT
    a,
    b,
    c
FROM TEXT.`//root/20{04, 05}.txt`;

-- JSON treated as Text File
SELECT
    a,
    b,
    c
FROM TEXT.`examples/src/main/resources/people.json`;

-- BinaryFile
SELECT
    a,
    b,
    c
FROM BINARYFILE.`/events/events-kafka.json`;

-- Directory of BinaryFiles
SELECT
    a,
    b,
    c
FROM BINARYFILE.`/events/events-kafka`;

-- CSV File
SELECT
    a,
    b,
    c
FROM CSV.`/sales/sales.csv`;

-- Delta File; test for Issue #602
SELECT
    a,
    b,
    c
FROM DELTA.`/mnt/datalake/table`;
