CREATE EXTERNAL TABLE hive_catalog.hive_db.external_hive_table
ENGINE=hive
PROPERTIES (
  'file_format' = 'orc',
  'external_location' = 'hdfs://namenode:9000/user/hive/warehouse/external_table'
)
AS SELECT * FROM source_table; 
