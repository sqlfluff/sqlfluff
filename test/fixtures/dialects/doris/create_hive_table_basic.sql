CREATE TABLE hive_catalog.hive_db.hive_table
(
    id INT,
    name STRING,
    age INT,
    email STRING
)
ENGINE=hive
PROPERTIES (
    'file_format' = 'parquet'
); 

