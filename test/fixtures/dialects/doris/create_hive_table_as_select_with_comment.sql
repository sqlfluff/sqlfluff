CREATE TABLE hive_catalog.hive_db.hive_table_with_comment
ENGINE=hive
COMMENT 'This is a Hive table created as select.'
PROPERTIES (
  'file_format' = 'parquet'
)
AS SELECT id, name FROM source_table; 

