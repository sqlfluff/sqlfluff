
select
    t1.field,
    extract(MILLENNIUM FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(CENTURY FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(DECADE FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(EPOCH FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(YEAR FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(ISOYEAR FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(QUARTER FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(MONTH FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(WEEK FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(ISOWEEK FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(ISODOW FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(DOW FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(DOY FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(DAY FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(HOUR FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(MINUTE FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(SECOND FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(MILLISECONDS FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(MICROSECONDS FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(TIME ZONE FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(TIMEZONE_HOUR FROM t1.sometime) AS a
from t1;

select
    t1.field,
    extract(TIMEZONE_MINUTE FROM t1.sometime) AS a
from t1;

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
