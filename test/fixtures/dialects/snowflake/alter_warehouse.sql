alter warehouse if exists wh1 rename to wh2;
alter warehouse my_wh set warehouse_size=medium;
alter warehouse LOAD_WH set warehouse_size = XXLARGE;
alter warehouse LOAD_WH set WAIT_FOR_COMPLETION = TRUE;
alter warehouse LOAD_WH set MAX_CLUSTER_COUNT = 5;
alter warehouse LOAD_WH set MIN_CLUSTER_COUNT = 1;

alter warehouse LOAD_WH set SCALING_POLICY = STANDARD;
alter warehouse LOAD_WH set SCALING_POLICY = 'STANDARD';
alter warehouse LOAD_WH set SCALING_POLICY = ECONOMY;
alter warehouse LOAD_WH set SCALING_POLICY = 'ECONOMY';


alter warehouse LOAD_WH set AUTO_SUSPEND = 1;
alter warehouse LOAD_WH set AUTO_RESUME = FALSE;
alter warehouse LOAD_WH set RESOURCE_MONITOR = monitor_name;
alter warehouse LOAD_WH set COMMENT = 'This is a comment';
alter warehouse LOAD_WH set MAX_CONCURRENCY_LEVEL = 1;
alter warehouse LOAD_WH set STATEMENT_QUEUED_TIMEOUT_IN_SECONDS = 300;
alter warehouse LOAD_WH set STATEMENT_TIMEOUT_IN_SECONDS = 300;
alter warehouse LOAD_WH set TAG thetag = 'tag1';
alter warehouse LOAD_WH set TAG thetag1 = 'tag1', thetag2 = 'tag2';
alter warehouse LOAD_WH RESUME IF SUSPENDED;
alter warehouse LOAD_WH ABORT ALL QUERIES;
alter warehouse LOAD_WH RENAME TO LOAD_WH2;
alter warehouse LOAD_WH SET MAX_CONCURRENCY_LEVEL = 1;
alter warehouse LOAD_WH UNSET STATEMENT_QUEUED_TIMEOUT_IN_SECONDS;
alter warehouse LOAD_WH UNSET WAREHOUSE_SIZE;
alter warehouse LOAD_WH UNSET WAREHOUSE_SIZE, WAIT_FOR_COMPLETION;

ALTER WAREHOUSE SET WAREHOUSE_SIZE='X-LARGE';
alter warehouse set warehouse_size=medium;

alter warehouse LOAD_WH set WAREHOUSE_TYPE = STANDARD;
alter warehouse LOAD_WH set WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED';

ALTER WAREHOUSE IDENTIFIER($var_wh) SET WAREHOUSE_TYPE = STANDARD;

