SELECT
    my_table.a,
    other_table.b
FROM my_table
LEFT JOIN other_table
    ON DATEDIFF(SECOND, my_table.timestamp_a, other_table.timestamp_b) > 1;

SELECT
    DATE_ADD(MICROSECOND, 5, start_dt) AS date_add_micro,
    DATE_DIFF(MILLISECOND, start_dt, end_dt) AS datediff_milli,
    DATEADD(MINUTE, 5, start_dt) AS dateadd_min,
    DATEDIFF(HOUR, start_dt, end_dt) AS datediff_hr,
    TIMEDIFF(DAY, start_dt, end_dt) AS timediff_day,
    TIMESTAMPADD(DAYOFYEAR, 5, start_dt) AS ts_add_day_of_yr,
    TIMESTAMPDIFF(WEEK, start_dt, end_dt) AS ts_diff_week,
    DATE_ADD(MONTH, 5, start_dt) AS date_add_month,
    DATE_ADD(QUARTER, 5, start_dt) AS date_add_quarter,
    DATE_ADD(YEAR, 5, start_dt) AS date_add_year
FROM my_table;
