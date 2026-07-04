CREATE TABLE t_kudu (id BIGINT, name STRING) STORED AS KUDU;

CREATE TABLE t_kudu_comment (id BIGINT, name STRING) COMMENT 'table comment' STORED AS KUDU;

CREATE TABLE t_kudu_pk (id BIGINT, business_date STRING, name STRING, PRIMARY KEY (id, business_date)) STORED AS KUDU;

CREATE TABLE t_kudu_pk_comment (id BIGINT, business_date STRING, name STRING, PRIMARY KEY (id, business_date)) COMMENT 'kudu table with primary key' STORED AS KUDU;
