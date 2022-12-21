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
