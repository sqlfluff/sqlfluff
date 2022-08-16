SELECT DATEADD(NANOSECONDS, -1, '2020-01-01');

-- https://docs.snowflake.com/en/sql-reference/data-types-datetime.html#interval-examples

select to_date('2018-04-15') + INTERVAL '1 year';

select to_time('04:15:29') + INTERVAL '3 hours, 18 minutes';

select current_timestamp + INTERVAL
                           '1 year, 3 quarters, 4 months, 5 weeks, 6 days, 7 minutes, 8 seconds,
                            1000 milliseconds, 4000000 microseconds, 5000000001 nanoseconds'
                        as complex_interval1;

select to_date('2025-01-17') + INTERVAL
                               '1 y, 3 q, 4 mm, 5 w, 6 d, 7 h, 9 m, 8 s,
                                1000 ms, 445343232 us, 898498273498 ns'
                            as complex_interval2;

select name, hire_date from employees where hire_date > current_date - INTERVAL '2 y, 3 month';

select ts + INTERVAL '4 seconds' from t1 where ts > to_timestamp('2014-04-05 01:02:03');
