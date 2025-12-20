-- ANSI-inherited ALTER TABLE operations
ALTER TABLE x DROP COLUMN y;
ALTER TABLE x DROP y;

-- ADD COLUMNS (basic and with PARTITION)
ALTER TABLE table_name ADD COLUMNS (col_name int);
ALTER TABLE table_name ADD COLUMNS (col1 varchar(50), col2 int, col3 boolean);
ALTER TABLE table_name PARTITION (partition_col1_name = 'value1') ADD COLUMNS (col_name int);
ALTER TABLE table_name PARTITION (partition_col1_name = 'value1', partition_col2_name = 'value2') ADD COLUMNS (col1 varchar(50), col2 int);

-- ADD PARTITION
ALTER TABLE orders ADD PARTITION (dt = '2016-05-14', country = 'IN');
ALTER TABLE orders ADD IF NOT EXISTS PARTITION (dt = '2016-05-31', country = 'IN') LOCATION 's3://amzn-s3-demo-bucket/path/to/INDIA_31_May_2016/';
ALTER TABLE orders ADD PARTITION (dt = '2016-05-31', country = 'IN') PARTITION (dt = '2016-06-01', country = 'IN');

-- CHANGE COLUMN
ALTER TABLE example_table CHANGE COLUMN area zip int AFTER id;
ALTER TABLE example_table CHANGE zip zip int COMMENT 'USA zipcode';
ALTER TABLE my_table CHANGE old_col new_col string FIRST;

-- DROP PARTITION
ALTER TABLE orders DROP PARTITION (dt = '2014-05-14', country = 'IN');
ALTER TABLE orders DROP IF EXISTS PARTITION (dt = '2014-05-14', country = 'IN'), PARTITION (dt = '2014-05-15', country = 'IN');

-- RENAME PARTITION
ALTER TABLE orders PARTITION (dt = '2014-05-14', country = 'IN') RENAME TO PARTITION (dt = '2014-05-15', country = 'IN');

-- REPLACE COLUMNS (basic and with PARTITION)
ALTER TABLE names_cities REPLACE COLUMNS (first_name string, last_name string, city string);
ALTER TABLE partitioned_table PARTITION (year = 2023) REPLACE COLUMNS (new_col1 int, new_col2 string);

-- SET LOCATION (basic and with PARTITION)
ALTER TABLE my_table SET LOCATION 's3://my-bucket/new-location/';
ALTER TABLE my_table PARTITION (dt = '2023-01-01') SET LOCATION 's3://my-bucket/partition-location/';

-- SET TBLPROPERTIES
ALTER TABLE my_table SET TBLPROPERTIES ('property_name' = 'property_value');
ALTER TABLE my_table SET TBLPROPERTIES ('property_name' = 'property_value', 'another_prop' = 'another_value');
