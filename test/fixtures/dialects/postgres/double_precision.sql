-- This ensures DOUBLE and PRECISION are never concatenated

-- Basic ALTER TABLE with multiple columns
ALTER TABLE t
ADD COLUMN a double precision,
ADD COLUMN b double precision,
ADD COLUMN v double precision;

-- CREATE TABLE with DOUBLE PRECISION
CREATE TABLE test_double_precision (
    id serial PRIMARY KEY,
    value1 double precision,
    value2 double precision NOT NULL,
    value3 double precision DEFAULT 0.0
);

-- Function with DOUBLE PRECISION parameters
CREATE FUNCTION calculate_area(
    width double precision,
    height double precision
) RETURNS double precision AS $$
BEGIN
    RETURN width * height;
END;
$$ LANGUAGE plpgsql;

-- Casting to DOUBLE PRECISION
SELECT
    column1::double precision,
    column2::double precision AS calculated_value
FROM my_table;

-- Mixed case (should preserve case)
ALTER TABLE t ADD COLUMN mixed_case double precision;

-- Complex ALTER TABLE with constraints
ALTER TABLE measurements
ADD COLUMN temperature double precision NOT NULL,
ADD COLUMN pressure double precision DEFAULT 101.325,
ADD COLUMN humidity double precision CONSTRAINT valid_humidity CHECK (
    humidity BETWEEN 0 AND 100
);

-- DOUBLE PRECISION in array context
CREATE TABLE array_test (
    all_values double precision [],
    matrix double precision [] [],
    single_value double precision
);

-- DOUBLE PRECISION with multiple spaces (should normalize to single space)
ALTER TABLE t ADD COLUMN spaced double precision;

-- DOUBLE PRECISION with tab (should normalize to single space)
ALTER TABLE t ADD COLUMN tabbed double precision;
