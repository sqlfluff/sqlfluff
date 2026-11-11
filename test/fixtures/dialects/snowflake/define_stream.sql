DEFINE STREAM my_db.public.my_stream
    ON TABLE my_db.public.my_table
    APPEND_ONLY = TRUE;

DEFINE STREAM "my view stream"
    ON VIEW my_view
    APPEND_ONLY = FALSE
    SHOW_INITIAL_ROWS = TRUE
    COMMENT = 'View changes';

DEFINE STREAM external_stream
    ON EXTERNAL TABLE external_table
    INSERT_ONLY = TRUE;

DEFINE STREAM stage_stream ON STAGE my_stage;

DEFINE STREAM event_stream ON EVENT TABLE my_events;

DEFINE STREAM dynamic_stream ON DYNAMIC TABLE my_dynamic_table;
