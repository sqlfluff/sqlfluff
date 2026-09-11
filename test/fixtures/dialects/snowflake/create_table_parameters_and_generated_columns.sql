-- CREATE TABLE parameters and generated columns
-- https://docs.snowflake.com/en/sql-reference/sql/create-table

CREATE TABLE t_schema_evolution (c INT) ENABLE_SCHEMA_EVOLUTION = TRUE;

CREATE TABLE t_schema_evolution_off (c INT) ENABLE_SCHEMA_EVOLUTION = FALSE;

CREATE TABLE t_row_timestamp (a INT) ROW_TIMESTAMP = TRUE;

CREATE TABLE t_error_logging (a INT) ERROR_LOGGING = TRUE;

CREATE TABLE t_iceberg_collation (a INT) ICEBERG_DEFAULT_DDL_COLLATION = 'en-ci';

CREATE TABLE t_many_params (a INT)
ENABLE_SCHEMA_EVOLUTION = TRUE
DATA_RETENTION_TIME_IN_DAYS = 5
CHANGE_TRACKING = TRUE
ROW_TIMESTAMP = FALSE
COMMENT = 'lots of parameters';

CREATE TABLE t_generated (a INT, b INT GENERATED ALWAYS AS (a + 1));

CREATE TABLE t_generated_virtual (
    a INT,
    b NUMBER(10, 2) GENERATED ALWAYS AS (a * 2) VIRTUAL,
    c STRING AS (TO_VARCHAR(a))
);

CREATE TEMP READ ONLY TABLE t_read_only_clone CLONE source_table;

CREATE TEMPORARY READ ONLY TABLE t_read_only_temporary CLONE source_table;

CREATE LOCAL TEMP READ ONLY TABLE t_read_only_local CLONE source_table;

CREATE OR REPLACE TABLE t_check_out_of_line (
    a INT,
    b INT,
    CONSTRAINT chk_a CHECK (a < 100),
    CHECK (b > 0)
);

CREATE TABLE t_check_enable_validate (
    a INT,
    CONSTRAINT chk_a CHECK (a < 100) ENABLE VALIDATE
);

CREATE TABLE t_inline_references (
    c INT REFERENCES other_table (x) MATCH FULL ON DELETE CASCADE,
    d INT REFERENCES other_table (y) MATCH SIMPLE ON UPDATE SET NULL,
    e INT REFERENCES other_table (z) NOT ENFORCED RELY
);
