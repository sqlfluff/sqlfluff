SELECT item, purchases, category, LAST_VALUE(item)
  OVER (c) AS most_popular
FROM Produce
WINDOW
  a AS (PARTITION BY category),
  b AS (ORDER BY purchases),
  c AS (ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING)
