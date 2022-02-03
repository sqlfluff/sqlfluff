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
