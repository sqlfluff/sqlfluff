CREATE TABLE t_ctas STORED AS PARQUET AS SELECT id, name FROM source_table;

CREATE TABLE t_ctas_part PARTITIONED BY (partition_code) STORED AS PARQUET AS SELECT id, name, partition_code FROM source_table;
