CREATE TABLE t_part_parquet (id BIGINT, name STRING) PARTITIONED BY (partition_code STRING COMMENT 'technical partition') STORED AS PARQUET;

CREATE TABLE t_part_comment_parquet (id BIGINT, name STRING) PARTITIONED BY (partition_code STRING COMMENT 'technical partition') COMMENT 'table comment' STORED AS PARQUET;

CREATE TABLE t_tblprops (id BIGINT, name STRING) STORED AS PARQUET TBLPROPERTIES ("transactional" = "false");

CREATE TABLE t_full_tail (id BIGINT, name STRING) PARTITIONED BY (partition_code STRING COMMENT 'technical partition') COMMENT 'table comment' STORED AS PARQUET TBLPROPERTIES ("transactional" = "false");
