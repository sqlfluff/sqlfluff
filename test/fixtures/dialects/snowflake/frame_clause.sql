SELECT
  a,
  LAST_VALUE(foo)
    IGNORE NULLS OVER (
      PARTITION BY bar
      ORDER BY baz ASC
      ROWS BETWEEN $my_var PRECEDING AND CURRENT ROW
  ) AS vehicle_type_id_last_value
FROM foo
;

SELECT
  account_id
  , SUM(amount)
    OVER (ORDER BY date_created RANGE BETWEEN INTERVAL '7 DAYS' PRECEDING AND CURRENT ROW)
    AS trailing_7d_sum_amount
FROM my_database.my_schema.my_table
;
