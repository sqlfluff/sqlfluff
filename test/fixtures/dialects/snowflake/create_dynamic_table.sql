CREATE OR REPLACE DYNAMIC TABLE names(
  id,
  first_name,
  last_name
)
REFRESH_MODE = AUTO
TARGET_LAG = '1 minute'
INITIALIZE = ON_CREATE
WAREHOUSE = 'mywh'
AS
SELECT var:id::int id, var:fname::string first_name,
var:lname::string last_name FROM raw;


CREATE OR REPLACE DYNAMIC TABLE product
  TARGET_LAG = '20 minutes'
  WAREHOUSE = mywh
  AS
    SELECT product_id, product_name FROM staging_table;


CREATE DYNAMIC ICEBERG TABLE product (date TIMESTAMP_NTZ, id NUMBER, content STRING)
  TARGET_LAG = '20 minutes'
  WAREHOUSE = mywh
  EXTERNAL_VOLUME = 'my_external_volume'
  CATALOG = 'SNOWFLAKE'
  BASE_LOCATION = 'my_iceberg_table'
  AS
    SELECT product_id, product_name FROM staging_table;

CREATE DYNAMIC TABLE product (date TIMESTAMP_NTZ, id NUMBER, content VARIANT)
  TARGET_LAG = '20 minutes'
  WAREHOUSE = mywh
  CLUSTER BY (date, id)
  AS
    SELECT product_id, product_name FROM staging_table;

CREATE DYNAMIC TABLE product_clone CLONE product AT (TIMESTAMP => TO_TIMESTAMP_TZ('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));

CREATE DYNAMIC TABLE product
  TARGET_LAG = 'DOWNSTREAM'
  WAREHOUSE = mywh
  INITIALIZE = on_schedule
  REQUIRE USER
  AS
    SELECT product_id, product_name FROM staging_table;


-- Test INITIALIZATION_WAREHOUSE
CREATE DYNAMIC TABLE init_warehouse_test
  TARGET_LAG = '1 minute'
  WAREHOUSE = mywh
  INITIALIZATION_WAREHOUSE = init_wh
  AS
    SELECT id FROM raw;

-- Test AGGREGATION POLICY
CREATE DYNAMIC TABLE agg_policy_test
  TARGET_LAG = '1 minute'
  WAREHOUSE = mywh
  WITH AGGREGATION POLICY my_agg_policy ENTITY KEY (id)
  AS
    SELECT id FROM raw;

-- Test ROW ACCESS POLICY (moved from dynamic options)
CREATE DYNAMIC TABLE row_policy_test
  TARGET_LAG = '1 minute'
  WAREHOUSE = mywh
  WITH ROW ACCESS POLICY my_row_policy ON (id)
  AS
    SELECT id FROM raw;

-- Test mixed options (COMMENT, DATA_RETENTION)
CREATE DYNAMIC TABLE mixed_options_test
  TARGET_LAG = '1 minute'
  WAREHOUSE = mywh
  DATA_RETENTION_TIME_IN_DAYS = 1
  COMMENT = 'This is a test'
  AS
    SELECT id FROM raw;

-- Test CLUSTER BY (verified placement)
CREATE DYNAMIC TABLE cluster_by_test
  TARGET_LAG = '1 minute'
  WAREHOUSE = mywh
  CLUSTER BY (id)
  AS
    SELECT id FROM raw;
