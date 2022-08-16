CREATE TABLE masonboro_sandbox.test
AS
WITH us_sales
AS (
    SELECT rev
    FROM masonboro_sales.us_2021
)

SELECT rev
FROM us_sales;
