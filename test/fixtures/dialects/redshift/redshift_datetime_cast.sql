-- redshift_datetime_cast.sql
/* Example that casts a column to several DATETIME types */

-- from https://github.com/sqlfluff/sqlfluff/issues/2649
SELECT b::DATETIME
FROM a;

-- DATE
SELECT b::DATE
FROM a;

-- TIME
SELECT
    b::TIME,
    c::TIME WITH TIME ZONE,
    d::TIME WITHOUT TIME ZONE
FROM a;

-- TIMETZ
SELECT b::TIMETZ
FROM a;

-- TIMESTAMP
SELECT
    b::TIMESTAMP,
    c::TIMESTAMP WITHOUT TIME ZONE,
    d::TIMESTAMP WITH TIME ZONE
FROM a;

-- TIMESTAMPTZ
SELECT
    b::TIMESTAMPTZ
FROM a;
