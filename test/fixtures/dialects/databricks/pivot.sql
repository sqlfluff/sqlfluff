-- Examples from https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-qry-select-pivot.html

-- A very basic PIVOT
-- Given a table with sales by quarter, return a table that returns sales across quarters per year.
SELECT year, region, q1, q2, q3, q4
FROM sales
PIVOT (sum(sales) AS sales
  FOR quarter
  IN (1 AS q1, 2 AS q2, 3 AS q3, 4 AS q4));

-- Also PIVOT on region
SELECT year, q1_east, q1_west, q2_east, q2_west, q3_east, q3_west, q4_east, q4_west
FROM sales
PIVOT (sum(sales) AS sales
  FOR (quarter, region)
  IN ((1, 'east') AS q1_east, (1, 'west') AS q1_west, (2, 'east') AS q2_east, (2, 'west') AS q2_west,
      (3, 'east') AS q3_east, (3, 'west') AS q3_west, (4, 'east') AS q4_east, (4, 'west') AS q4_west));

-- To aggregate across regions the column must be removed from the input.
SELECT year, q1, q2, q3, q4
FROM (SELECT year, quarter, sales FROM sales) AS s
PIVOT (sum(sales) AS sales
  FOR quarter
  IN (1 AS q1, 2 AS q2, 3 AS q3, 4 AS q4));

-- A PIVOT with multiple aggregations
SELECT year, q1_total, q1_avg, q2_total, q2_avg, q3_total, q3_avg, q4_total, q4_avg
  FROM (SELECT year, quarter, sales FROM sales) AS s
  PIVOT (sum(sales) AS total, avg(sales) AS avg
    FOR quarter
    IN (1 AS q1, 2 AS q2, 3 AS q3, 4 AS q4));
