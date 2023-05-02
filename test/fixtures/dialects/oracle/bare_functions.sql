SELECT
  a.foo,
  b.bar,
  current_date,
  current_timestamp,
  dbtimezone,
  localtimestamp,
  sessiontimestamp,
  sysdate,
  systimestamp
FROM first_table a
INNER JOIN second_table b
ON a.baz = b.baz
;
