SELECT timestamp with time zone '2005-04-02 12:00:00-07' + interval '1 day';

SELECT DATEADD(day, -2, current_date);

SELECT timestamptz '2013-07-01 12:00:00' - timestamptz '2013-03-01 12:00:00';

SELECT 1.0::int;

SELECT '2015-10-24 16:38:46'::TIMESTAMP;

SELECT '2015-10-24 16:38:46'::TIMESTAMP AT TIME ZONE 'UTC';

SELECT '2015-10-24 16:38:46'::TIMESTAMP WITH TIME ZONE;

SELECT '2015-10-24 16:38:46'::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'UTC';

SELECT '2015-10-24 16:38:46'::TIMESTAMP WITHOUT TIME ZONE;

SELECT '2015-10-24 16:38:46'::TIMESTAMPTZ;

SELECT '2015-10-24 16:38:46'::TIMESTAMPTZ AT TIME ZONE 'UTC';

-- Some more example from https://database.guide/how-at-time-zone-works-in-postgresql/

SELECT timestamp with time zone '2025-11-20 00:00:00+00' AT TIME ZONE 'Africa/Cairo';

SELECT timestamp with time zone '2025-11-20 00:00:00';

SELECT timestamp without time zone '2025-11-20 00:00:00' AT TIME ZONE 'Africa/Cairo';

SELECT timestamp without time zone '2025-11-20 00:00:00+12' AT TIME ZONE 'Africa/Cairo';

SELECT timestamp without time zone '2025-11-20 00:00:00+12';

SELECT time with time zone '00:00:00+00' AT TIME ZONE 'Africa/Cairo';

SELECT time without time zone '00:00:00' AT TIME ZONE 'Africa/Cairo';

SELECT c_timestamp AT TIME ZONE 'Africa/Cairo' FROM t_table;

SELECT (c_timestamp AT TIME ZONE 'Africa/Cairo')::time FROM t_table;

SELECT a::double precision FROM my_table;
