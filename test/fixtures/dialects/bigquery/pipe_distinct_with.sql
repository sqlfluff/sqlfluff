(
  SELECT 'apples' AS item, 2 AS sales
  UNION ALL
  SELECT 'bananas' AS item, 5 AS sales
  UNION ALL
  SELECT 'bananas' AS item, 5 AS sales
)
|> DISTINCT
|> WHERE sales >= 3;

FROM foo
|> DISTINCT;

SELECT 1 AS key
|> WITH t AS (SELECT 1 AS key, 'my_value' AS value)
|> INNER JOIN t USING (key);

SELECT 1 AS key
|> WITH t1 AS (SELECT 2), t2 AS (SELECT 3)
|> UNION ALL (FROM t1), (FROM t2);

SELECT 1 AS key
|> WITH t1 AS (SELECT 2), t2 AS (SELECT 3),
|> UNION ALL (FROM t1), (FROM t2);
