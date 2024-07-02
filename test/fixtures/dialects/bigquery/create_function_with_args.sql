CREATE FUNCTION example_dataset.exampleFunction(x FLOAT64)
RETURNS FLOAT64
AS (x * x);

CREATE OR REPLACE FUNCTION `example-project.example_dataset.exampleFunction`(x INTEGER, y INTEGER)
RETURNS INTEGER
AS (x * y)
OPTIONS(description="foo");

CREATE TEMPORARY FUNCTION exampleFunction(x BIGNUMERIC)
AS (x + x);

CREATE TEMP FUNCTION exampleFunction(x STRING)
RETURNS STRING
AS (CONCAT(x, x))
OPTIONS();
