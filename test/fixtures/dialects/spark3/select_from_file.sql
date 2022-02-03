-- PARQUET file
SELECT
    a,
    b,
    c
FROM parquet.`examples/src/main/resources/users.parquet`;

-- Directory of Parquet Files
SELECT
    a,
    b,
    c
FROM parquet.`examples/src/main/resources/users`;

-- ORC file
SELECT
    a,
    b,
    c
FROM orc.`examples/src/main/resources/users.orc`;

-- JSON file
SELECT
    a,
    b,
    c
FROM json.`examples/src/main/resources/people.json`;

-- Directory of JSON files
SELECT
    a,
    b,
    c
FROM json.`examples/src/main/resources/people`;

-- Text File
SELECT
    a,
    b,
    c
FROM text.`examples/src/main/resources/people.txt`;

-- JSON treated as Text File
SELECT
    a,
    b,
    c
FROM text.`examples/src/main/resources/people.json`;

-- BinaryFile
SELECT
    a,
    b,
    c
FROM binaryfile.`/events/events-kafka.json`;

-- Directory of BinaryFiles
SELECT
    a,
    b,
    c
FROM binaryfile.`/events/events-kafka`;

-- CSV File
SELECT
    a,
    b,
    c
FROM csv.`/sales/sales.csv`;

-- Delta File; test for Issue #602
SELECT
    a,
    b,
    c
FROM delta.`/mnt/datalake/table`;
