ALTER TABLE hr.tables.empl_info
    ADD DATA METRIC FUNCTION snowflake.core.null_count ON (email);

ALTER TABLE t
    ADD DATA METRIC FUNCTION snowflake.core.duplicate_count ON (id),
        snowflake.core.null_count ON (email);

ALTER TABLE t
    ADD DATA METRIC FUNCTION governance.dmfs.count_positive ON (amount)
    EXPECTATION amount_ok (VALUE = 0), recent_ok (VALUE < 10)
    EXECUTE AS ROLE dq_role;

ALTER TABLE t
    ADD DATA METRIC FUNCTION snowflake.core.null_count ON (email)
    FILTER (region = 'EU');

ALTER TABLE t
    ADD DATA METRIC FUNCTION snowflake.core.row_count ON ()
    WITHIN GROUP (region, country) GROUP LIMIT 100;

ALTER TABLE t
    ADD DATA METRIC FUNCTION snowflake.core.row_count ON ()
    ANOMALY_DETECTION = TRUE
    SENSITIVITY = 'HIGH';

ALTER TABLE orders
    ADD DATA METRIC FUNCTION governance.dmfs.referential_check
    ON (customer_id, TABLE my_db.my_schema.customers (id));

ALTER TABLE t
    DROP DATA METRIC FUNCTION snowflake.core.null_count ON (email);

ALTER TABLE t
    DROP DATA METRIC FUNCTION snowflake.core.null_count ON (email),
        snowflake.core.duplicate_count ON (id);

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.null_count ON (email) SUSPEND;

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.null_count ON (email) RESUME,
        snowflake.core.duplicate_count ON (id) SUSPEND;

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION governance.dmfs.count_positive ON (amount)
    ADD EXPECTATION amount_ok (VALUE = 0);

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION governance.dmfs.count_positive ON (amount)
    MODIFY EXPECTATION amount_ok (VALUE <= 5);

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION governance.dmfs.count_positive ON (amount)
    DROP EXPECTATION amount_ok, recent_ok;

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.null_count ON (email)
    FILTER (region = 'US');

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.null_count ON (email)
    FILTER ();

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.row_count
    SET ANOMALY_DETECTION = FALSE SENSITIVITY = 'LOW' DATA_QUALITY_NOTIFICATION = TRUE;

ALTER TABLE t SET DATA_METRIC_SCHEDULE = 'USING CRON 0 8 * * * UTC';

ALTER TABLE t UNSET DATA_METRIC_SCHEDULE;

ALTER TABLE t
    MODIFY DATA METRIC FUNCTION snowflake.core.row_count
    SET SENSITIVITY = HIGH;
