ALTER VIEW my_view
    ADD DATA METRIC FUNCTION snowflake.core.null_count ON (email);

ALTER VIEW IF EXISTS my_db.my_schema.my_view
    DROP DATA METRIC FUNCTION snowflake.core.null_count ON (email);

ALTER VIEW my_view
    MODIFY DATA METRIC FUNCTION snowflake.core.null_count ON (email) SUSPEND;

ALTER VIEW my_view SET DATA_METRIC_SCHEDULE = '5 MINUTE';

ALTER VIEW my_view SET DATA_METRIC_SCHEDULE = 'USING CRON 0 8 * * * UTC';

ALTER VIEW my_view UNSET DATA_METRIC_SCHEDULE;
