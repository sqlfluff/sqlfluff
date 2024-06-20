create table awsdatacatalog.db.iceberg_table
with (
  table_type='iceberg',
  is_external=false,
  location='s3://bucket/prefix',
  format='parquet',
  vacuum_max_snapshot_age_seconds=86400
) 
as
select * from db.table
