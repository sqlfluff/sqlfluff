SELECT
 cast(field_1 as time with time zone),
 cast(field_2 as timestamp with time zone),
 CAST(CURRENT_TIMESTAMP AS TIMESTAMP(6) WITH TIME ZONE) AS _log_time,
FROM my_table;
