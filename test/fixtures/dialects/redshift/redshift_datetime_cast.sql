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

--- AT TIME ZONE
SELECT
    raw_data.status::VARCHAR AS status,
    raw_data.start::TIMESTAMPTZ AT TIME ZONE 'UTC' AS started_at,
    raw_data."end"::TIMESTAMPTZ AT TIME ZONE 'UTC' AS ended_at,
    raw_data.created::TIMESTAMPTZ AT TIME ZONE 'UTC' AS created_at,
    raw_data.identifier[0].value::VARCHAR AS communication_request_fhir_reference_origin,
    extension_extraction.database_reference,
    GETDATE() AT TIME ZONE 'UTC',
    (GETDATE() AT TIME ZONE 'UTC') AT TIME ZONE 'AEST',
    ((GETDATE() AT TIME ZONE 'UTC') AT TIME ZONE 'AEST')
FROM raw_data
