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
