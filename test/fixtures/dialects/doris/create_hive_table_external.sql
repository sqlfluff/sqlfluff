CREATE EXTERNAL TABLE hive_catalog.hive_db.external_table
(
    id INT,
    name STRING,
    data STRING
)
ENGINE=hive
PROPERTIES (
    'file_format' = 'orc'
); 

