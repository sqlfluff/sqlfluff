ALTER NOTEBOOK my_notebook RENAME TO notebook_v2;

ALTER NOTEBOOK IF EXISTS my_notebook RENAME TO my_db.my_schema.notebook_v2;

ALTER NOTEBOOK my_notebook SET COMMENT = 'amazing comment';

ALTER NOTEBOOK my_notebook SET QUERY_WAREHOUSE = my_wh;

ALTER NOTEBOOK my_notebook SET IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 7200;

ALTER NOTEBOOK my_notebook SET SECRETS = ('api_key' = my_db.my_schema.my_secret);

ALTER NOTEBOOK IF EXISTS my_db.my_schema.my_notebook SET
    QUERY_WAREHOUSE = my_wh
    IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 3600
    COMMENT = 'amazing comment';

ALTER NOTEBOOK my_notebook UNSET QUERY_WAREHOUSE;

ALTER NOTEBOOK my_notebook UNSET QUERY_WAREHOUSE, COMMENT;
