-- Create table if not exists
CREATE TABLE IF NOT EXISTS default.people10m (
    id INT,
    first_name STRING,
    middle_name STRING,
    last_name STRING,
    gender STRING,
    birth_date TIMESTAMP,
    ssn STRING,
    salary INT
) USING DELTA;

-- Create or replace table
CREATE OR REPLACE TABLE default.people10m (
    id INT,
    first_name STRING,
    middle_name STRING,
    last_name STRING,
    gender STRING,
    birth_date TIMESTAMP,
    ssn STRING,
    salary INT
) USING DELTA;

-- Create or replace table with path
CREATE OR REPLACE TABLE DELTA.`/delta/people10m` (
    id INT,
    first_name STRING,
    middle_name STRING,
    last_name STRING,
    gender STRING,
    birth_date TIMESTAMP,
    ssn STRING,
    salary INT
) USING DELTA;

-- Partition data
CREATE TABLE default.people10m (
    id INT,
    first_name STRING,
    middle_name STRING,
    last_name STRING,
    gender STRING,
    birth_date TIMESTAMP,
    ssn STRING,
    salary INT
)
USING DELTA
PARTITIONED BY (gender);

-- Control data location
CREATE TABLE default.people10m
USING DELTA
LOCATION '/delta/people10m';

-- Generated columns
CREATE TABLE default.people10m (
    id INT,
    first_name STRING,
    middle_name STRING,
    last_name STRING,
    gender STRING,
    birth_date TIMESTAMP,
    date_of_birth DATE GENERATED ALWAYS AS (CAST(birth_date AS DATE)),
    ssn STRING,
    salary INT
)
USING DELTA
PARTITIONED BY (gender);
