DEFINE TABLE db.sch.t (c INT);

ATTACH DATA METRIC FUNCTION snowflake.core.null_count
    TO TABLE db.sch.t
    ON (c)
    EXPECTATION t_c_not_null (VALUE = 0);

ATTACH DATA METRIC FUNCTION snowflake.core.avg
    TO VIEW db.sch.v
    ON (c)
    EXPECTATION v_c_avg (VALUE >= 0.9);

ATTACH DATA METRIC FUNCTION snowflake.core.null_count
    TO DYNAMIC TABLE db.sch.dt
    ON (c)
    EXPECTATION dt_c_not_null (VALUE = 0);

ATTACH DATA METRIC FUNCTION snowflake.core.duplicate_count
    TO TABLE db.sch.t
    ON (a, b)
    EXPECTATION t_pk (VALUE = 0);

ATTACH DATA METRIC FUNCTION snowflake.core.row_count
    TO TABLE db.sch.t
    ON ()
    EXPECTATION t_not_empty (VALUE > 0);

ATTACH DATA METRIC FUNCTION snowflake.core.null_percent
    TO TABLE db.sch.t
    ON (c);

SELECT 1 AS parsed_after_attachment;

ATTACH DATA METRIC FUNCTION db.sch.not_equal_count
    TO TABLE db.sch.t
    ON (a, b)
    EXPECTATION t_a_eq_b (VALUE = 0);

ATTACH DATA METRIC FUNCTION db.sch.f1
    TO TABLE db.sch.t1
    ON (a)
    EXECUTE AS ROLE ingest_admin;
