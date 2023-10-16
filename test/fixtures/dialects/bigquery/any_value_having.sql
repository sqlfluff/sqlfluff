SELECT
    ANY_VALUE(foo HAVING MIN bar) AS any_value_having_min,
    ANY_VALUE(foo HAVING MAX bar) AS any_value_having_max,
FROM t
