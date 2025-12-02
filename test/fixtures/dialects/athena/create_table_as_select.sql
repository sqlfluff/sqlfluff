CREATE TABLE my_ctas
WITH (
     format='Parquet',
     external_location='s3://my-bucket/my-path-level-1/my-path-level-2',
     partitioned_by=array['load_date']
    )
AS SELECT field_1, field_2, field_3 from my_table;
