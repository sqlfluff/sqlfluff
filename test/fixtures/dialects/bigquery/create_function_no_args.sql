CREATE FUNCTION add() RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

CREATE FUNCTION example_dataset.exampleFunction() RETURNS STRING
AS ("example")
OPTIONS(description="example");

CREATE TEMP FUNCTION exampleFunction() RETURNS FLOAT64
AS (1.234 * 5.678);

CREATE TEMPORARY FUNCTION exampleFunction() RETURNS BOOL
AS (TRUE)
OPTIONS();
