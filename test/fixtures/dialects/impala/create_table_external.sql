CREATE EXTERNAL TABLE t_external_location (id BIGINT, name STRING) STORED AS PARQUET LOCATION '/data/test/t_external_location';

CREATE EXTERNAL TABLE t_external_full (id BIGINT, name STRING) PARTITIONED BY (partition_code STRING) STORED AS PARQUET LOCATION '/data/test/t_external_full' TBLPROPERTIES ("transactional" = "false");
