-- Test singular and plural interval forms in DuckDB
-- DuckDB supports both singular and plural forms for interval datetime units

-- Simple interval expressions with both singular and plural
SELECT 
    INTERVAL 1 DAY,
    INTERVAL 1 DAYS,
    INTERVAL 3 WEEK,
    INTERVAL 3 WEEKS,
    INTERVAL 6 HOUR,
    INTERVAL 6 HOURS,
    INTERVAL 30 MINUTE,
    INTERVAL 30 MINUTES,
    INTERVAL 45 SECOND,
    INTERVAL 45 SECONDS,
    INTERVAL 1 MONTH,
    INTERVAL 1 MONTHS,
    INTERVAL 1 YEAR,
    INTERVAL 1 YEARS,
    INTERVAL 500 MILLISECOND,
    INTERVAL 500 MILLISECONDS,
    INTERVAL 1000 MICROSECOND,
    INTERVAL 1000 MICROSECONDS;

-- Window functions with interval ranges using plural forms
SELECT
  dts.start_time,
  count(*) OVER (ORDER BY dts.start_time) AS num,
  count(*)
    OVER (
      ORDER BY
        dts.start_time
      RANGE BETWEEN INTERVAL 3 WEEKS PRECEDING AND INTERVAL 6 HOURS PRECEDING
    ) AS num_roll
FROM
  range('2021-01-01'::DATE, '2021-01-02'::DATE, INTERVAL 1 HOUR)
    AS dts (start_time);

-- Interval arithmetic with plural forms
SELECT 
    current_timestamp + INTERVAL 1 DAYS AS tomorrow,
    current_timestamp - INTERVAL 7 DAYS AS last_week,
    current_timestamp + INTERVAL 2 WEEKS AS two_weeks_later,
    current_timestamp - INTERVAL 3 MONTHS AS three_months_ago;
