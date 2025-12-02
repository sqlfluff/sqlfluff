-- `HAVING` clause referring to column in `GROUP BY`.
SELECT
    city,
    sum(quantity) AS sum_quantity
FROM dealer GROUP BY city HAVING city = 'Fremont';

-- `HAVING` clause referring to aggregate function.
SELECT
    city,
    sum(quantity) AS sum_quantity
FROM dealer GROUP BY city HAVING sum(quantity) > 15;

-- `HAVING` clause referring to aggregate function
--   by its alias.
SELECT
    city,
    sum(quantity) AS sum_quantity
FROM dealer GROUP BY city HAVING sum_quantity > 15;

-- `HAVING` clause referring to a different aggregate
--   function than what is present in `SELECT` list.
SELECT
    city,
    sum(quantity) AS sum_quantity
FROM dealer GROUP BY city HAVING max(quantity) > 15;

-- `HAVING` clause referring to constant expression.
SELECT
    city,
    sum(quantity) AS sum_quantity
FROM dealer GROUP BY city HAVING 1 > 0 ORDER BY city;

-- `HAVING` clause without a `GROUP BY` clause.
SELECT sum(quantity) AS sum_quantity
FROM dealer HAVING sum(quantity) > 10;
