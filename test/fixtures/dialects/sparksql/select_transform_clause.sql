-- With specified output without data type
SELECT TRANSFORM (zip_code, name, age)
    USING 'cat' AS (a, b, c)
FROM person
WHERE zip_code > 94511;

-- With specified output with data type
SELECT TRANSFORM(zip_code, name, age)
    USING 'cat' AS (a string, b string, c string)
FROM person
WHERE zip_code > 94511;

-- Using ROW FORMAT DELIMITED
SELECT TRANSFORM(name, age)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    NULL DEFINED AS 'NULL'
    USING 'cat' AS (name_age string)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '@'
    LINES TERMINATED BY '\n'
    NULL DEFINED AS 'NULL'
FROM person;

-- Using Hive Serde
SELECT TRANSFORM(zip_code, name, age)
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
    WITH SERDEPROPERTIES (
        'field.delim' = '\t'
    )
    USING 'cat' AS (a string, b string, c string)
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
    WITH SERDEPROPERTIES (
        'field.delim' = '\t'
    )
FROM person
WHERE zip_code > 94511;

-- Schema-less mode
SELECT TRANSFORM(zip_code, name, age)
    USING 'cat'
FROM person
WHERE zip_code > 94500;
