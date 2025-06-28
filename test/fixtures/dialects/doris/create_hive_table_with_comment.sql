CREATE TABLE hive_catalog.hive_db.commented_table
(
    id INT COMMENT 'Primary key',
    name STRING COMMENT 'User name',
    age INT COMMENT 'User age',
    email STRING COMMENT 'User email address'
)
ENGINE=hive
COMMENT 'This is a test table for Hive catalog'
PROPERTIES (
    'file_format' = 'parquet',
    'hive.metastore.uris' = 'thrift://127.0.0.1:9083'
); 