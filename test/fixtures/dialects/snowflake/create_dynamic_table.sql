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

CREATE DYNAMIC TABLE product (
  product_id int COMMENT 'product id',
  product_name
)
  TARGET_LAG = '20 minutes'
  WAREHOUSE = mywh
  AS
    SELECT product_id, product_name FROM staging_table;

CREATE DYNAMIC TABLE product (
  product_id COMMENT 'product id',
  product_name,
  product_description TEXT,
  "product_price" COMMENT 'product price',
  product_stock NUMBER COMMENT 'product stock'
)
  TARGET_LAG = '20 minutes'
  WAREHOUSE = mywh
  AS
    SELECT
      product_id,
      product_name,
      product_description,
      product_price,
      product_stock
    FROM staging_table;
