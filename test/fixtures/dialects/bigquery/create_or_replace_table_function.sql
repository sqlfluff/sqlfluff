-- CREATE TABLE FUNCTION WITH BASIC SYNTAX
CREATE OR REPLACE TABLE FUNCTION ds.lchtablefunction (x int, y varchar) AS (
    SELECT
        id AS call_id,
        creation_date AS created_at
    FROM
        ds.data
)
