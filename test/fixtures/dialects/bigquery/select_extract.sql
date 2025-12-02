SELECT EXTRACT(HOUR FROM some_timestamp AT TIME ZONE "UTC");

SELECT EXTRACT(HOUR FROM some_timestamp AT TIME ZONE timezone_column);

WITH Input AS (SELECT TIMESTAMP("2008-12-25 05:30:00+00") AS timestamp_value)
SELECT
  EXTRACT(DAY FROM timestamp_value AT TIME ZONE "UTC") AS the_day_utc,
  EXTRACT(DAY FROM timestamp_value AT TIME ZONE "America/Los_Angeles") AS the_day_california
FROM Input;
