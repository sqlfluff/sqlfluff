SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
UNION ALL
SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
