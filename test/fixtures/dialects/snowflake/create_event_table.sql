CREATE EVENT TABLE my_events;
CREATE OR REPLACE EVENT TABLE IF NOT EXISTS my_database.my_schema.my_events;
CREATE EVENT TABLE IF NOT EXISTS log_trace_db.public.event_table;

CREATE OR REPLACE EVENT TABLE IF NOT EXISTS my_events
    CLUSTER BY (date, type)
    DATA_RETENTION_TIME_IN_DAYS = 5
    MAX_DATA_EXTENSION_TIME_IN_DAYS = 30
    CHANGE_TRACKING = FALSE
    DEFAULT_DDL_COLLATION = 'en-ci'
    COPY GRANTS
    WITH COMMENT = 'My events table'
    WITH ROW ACCESS POLICY sales_policy ON (type, region)
    WITH TAG (cost_center = 'sales')
;
