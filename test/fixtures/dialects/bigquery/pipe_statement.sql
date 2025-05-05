FROM Produce;

FROM (SELECT 'apples' AS item, 2 AS sales)
|> SELECT item AS fruit_name;

FROM (SELECT 'apples' AS item, 2 AS sales)
|> EXTEND item IN ('carrots', 'oranges') AS is_orange;

FROM (SELECT 2 AS x, 3 AS y) AS t
|> SET x = x * x, y = 8
|> SELECT t.x AS original_x, x, y;

FROM (SELECT 1 AS x, 2 AS y) AS t
|> DROP x
|> SELECT t.x AS original_x, y;

FROM (SELECT 1 AS x, 2 AS y) AS t
|> RENAME y AS renamed_y
|> SELECT *, t.y AS t_y;

FROM (SELECT 1 AS x, 2 AS y)
|> AS t
|> RENAME y AS renamed_y
|> SELECT *, t.y AS t_y;

FROM foo
|> WHERE sales >= 3
|> LIMIT 10 OFFSET 4
|> ORDER BY sales DESC;

FROM Produce
|> AGGREGATE SUM(sales) AS total_sales
   GROUP AND ORDER BY category, item DESC;

FROM Produce
|> AGGREGATE SUM(sales) AS total_sales
   GROUP BY category, item
|> ORDER BY category, item DESC;

FROM Produce
|> AGGREGATE SUM(sales) AS total_sales ASC
   GROUP BY item, category DESC;

FROM Produce
|> AGGREGATE SUM(sales) AS total_sales
   GROUP BY item, category
|> ORDER BY category DESC, total_sales;

FROM foo
|> UNION ALL
    (SELECT 1),
    (SELECT 2);

FROM foo
|> UNION DISTINCT
    (SELECT 1),
    (SELECT 2);

FROM foo
|> UNION ALL BY NAME
    (SELECT 20 AS two_digit, 2 AS one_digit);

FROM foo
|> INTERSECT DISTINCT
    (SELECT 1),
    (SELECT 2);

FROM foo
|> INTERSECT DISTINCT
    (SELECT * FROM UNNEST(ARRAY<INT64>[2, 3, 3, 5]) AS number),
    (SELECT * FROM UNNEST(ARRAY<INT64>[3, 3, 4, 5]) AS number);

FROM foo
|> EXCEPT DISTINCT
    (SELECT 1),
    (SELECT 2);

FROM foo
|> EXCEPT DISTINCT
    (SELECT * FROM UNNEST(ARRAY<INT64>[1, 2]) AS number),
    (SELECT * FROM UNNEST(ARRAY<INT64>[1, 4]) AS number);

FROM foo
|> EXCEPT DISTINCT BY NAME
    (SELECT 10 AS two_digit, 1 AS one_digit);

FROM foo
|> LEFT JOIN
     (
       SELECT "apples" AS item, 123 AS id
     ) AS produce_data
   ON produce_sales.item = produce_data.item
|> SELECT produce_sales.item, sales, id;

FROM input_table
|> CALL tvf1(arg1)
|> CALL tvf2(arg2, arg3);

FROM mydataset.Produce
|> CALL APPENDS(NULL, NULL);

FROM LargeTable
|> TABLESAMPLE SYSTEM (1 PERCENT);

FROM foo
|> PIVOT(SUM(sales) FOR quarter IN ('Q1', 'Q2'));

FROM foo
|> UNPIVOT(sales FOR quarter IN (Q1, Q2));

SELECT * FROM UNNEST(ARRAY<INT64>[1, 2, 3]) AS number
|> UNION DISTINCT
    (SELECT 1),
    (SELECT 2);

WITH
  NumbersTable AS (
    SELECT 1 AS one_digit, 10 AS two_digit
    UNION ALL
    SELECT 2, 20
    UNION ALL
    SELECT 3, 30
  )
SELECT one_digit, two_digit FROM NumbersTable
|> INTERSECT DISTINCT BY NAME
    (SELECT 10 AS two_digit, 1 AS one_digit);

(
  SELECT 'apples' AS item, 2 AS sales
  UNION ALL
  SELECT 'bananas' AS item, 5 AS sales
  UNION ALL
  SELECT 'apples' AS item, 7 AS sales
)
|> AGGREGATE COUNT(*) AS num_items, SUM(sales) AS total_sales;

(
  SELECT "000123" AS id, "apples" AS item, 2 AS sales
  UNION ALL
  SELECT "000456" AS id, "bananas" AS item, 5 AS sales
) AS sales_table
|> AGGREGATE SUM(sales) AS total_sales GROUP BY id, item
-- The sales_table alias is now out of scope. We must introduce a new one.
|> AS t1
|> JOIN (SELECT 456 AS id, "yellow" AS color) AS t2
   ON CAST(t1.id AS INT64) = t2.id
|> SELECT t2.id, total_sales, color;

SELECT 1 AS x, 2 AS y, 3 AS z
|> AS t
|> RENAME y AS renamed_y
|> SELECT *, t.y AS t_y;

(
  SELECT 'apples' AS item, 2 AS sales
  UNION ALL
  SELECT 'carrots' AS item, 8 AS sales
)
|> EXTEND item IN ('carrots', 'oranges') AS is_orange;
