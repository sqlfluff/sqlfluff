-- Trino supports timestamp datatypes at various levels of
-- precision from TIMESTAMP(0) to TIMESTAMP(12). These
-- correspond to precision from seconds to picoseconds.
-- Bare TIMESTAMP is an alias for TIMESTAMP(3).
-- https://trino.io/docs/current/language/types.html#timestamp
-- https://trino.io/docs/current/language/types.html#timestamp-p

-- Basic Timestamp
SELECT CAST((TIMESTAMP '2012-10-31 01:00 UTC') AS TIMESTAMP);

-- Timestamp with minimum precision (seconds)
SELECT CAST((TIMESTAMP '2012-10-31 01:00 UTC') AS TIMESTAMP(0));

-- Timestamp with maximum precision (picoseconds)
SELECT CAST((TIMESTAMP '2012-10-31 01:00 UTC') AS TIMESTAMP(12));

-- Timestamp with time zone
SELECT
    CAST(
        (TIMESTAMP '2001-08-22 03:04:05.321 America/Chicago')
        AS TIMESTAMP WITH TIME ZONE
    );

-- Timestamp without time zone
SELECT
    CAST(
        (TIMESTAMP '2001-08-22 03:04:05.321 America/Chicago')
        AS TIMESTAMP WITHOUT TIME ZONE
    );

-- Timestamp with precision and time zone
SELECT
    CAST(
        (TIMESTAMP '2001-08-22 03:04:05.321 America/Chicago')
        AS TIMESTAMP(6) WITH TIME ZONE
    );

-- Timestamp with precision and without time zone
SELECT
    CAST(
        (TIMESTAMP '2001-08-22 03:04:05.321 America/Chicago')
        AS TIMESTAMP(6) WITHOUT TIME ZONE
    );
