SELECT
    t1.field,
    EXTRACT(CENTURY FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(DECADE FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(DOW FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(DOY FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(EPOCH FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(ISODOW FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(ISOYEAR FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(MICROSECONDS FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(MILLENNIUM FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(MILLISECONDS FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(TIMEZONE FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(TIMEZONE_HOUR FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    EXTRACT(TIMEZONE_MINUTE FROM t1.sometime) AS a
FROM t1;

SELECT
    t1.field,
    DATE '2001-09-28' + 7 + t1.data AS a
FROM t1;

SELECT
    t1.field,
    NOW() + INTERVAL '1 HOUR' + t1.data AS a
FROM t1;

SELECT
    t1.field,
    t1.data + TIME '03:00' AS a
FROM t1;

SELECT
    t1.field,
    INTERVAL '1 DAY' + INTERVAL '1 HOUR 2 MINUTES' + t1.data AS a
FROM t1;

SELECT
    t1.field,
    TIMESTAMP '2001-09-28 01:00' + INTERVAL '23 HOURS' + t1.data AS a
FROM t1;

SELECT
    t1.field,
    TIME '01:00' + INTERVAL '3S' + t1.data AS a
FROM t1;

SELECT
    t1.field,
    - INTERVAL '23 HOURS' + t1.data AS a
FROM t1;

SELECT
    t1.field,
    INTERVAL '1 HOUR' / 1.5 + t1.data AS a
FROM t1;

SELECT
    t1.field,
    INTERVAL '1' HOUR * 3.5 + t1.data AS a
FROM t1;


SELECT
    t1.field,
    TIMESTAMP WITH TIME ZONE '2005-04-02 12:00:00-07' + INTERVAL '24 HOURS' + t1.data AS a
FROM t1;
