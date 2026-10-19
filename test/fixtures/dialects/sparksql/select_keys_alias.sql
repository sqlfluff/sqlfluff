-- KEYS is not reserved, so it can be a column or table alias.
SELECT map_keys(m) AS keys FROM t;

SELECT keys.a FROM x AS keys LEFT JOIN y ON keys.id = y.id;

SELECT keys.a FROM x keys LEFT JOIN y ON keys.id = y.id;
