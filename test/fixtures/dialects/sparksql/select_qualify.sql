SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
QUALIFY rank <= 3;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
ORDER BY item;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
LIMIT 5;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
ORDER BY item
LIMIT 5;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
QUALIFY rank <= 3
LIMIT 5;

SELECT
  item,
  RANK() OVER (PARTITION BY category ORDER BY purchases DESC) AS rank
FROM Produce
WHERE Produce.category = 'vegetable'
WINDOW item_window AS (
  PARTITION BY category
  ORDER BY purchases
  ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING)
QUALIFY rank <= 3
ORDER BY item;

SELECT CURRENT_DATE() AS p_data_date
QUALIFY ROW_NUMBER() OVER (ORDER BY p_data_date) = 1;
