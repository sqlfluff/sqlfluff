CREATE TABLE hive_catalog.hive_db.hive_table
ENGINE=hive
PROPERTIES (
  'file_format' = 'parquet',
  'hive.metastore.uris' = 'thrift://127.0.0.1:9083'
)
AS SELECT * FROM source_table; 

