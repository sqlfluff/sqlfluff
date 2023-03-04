CREATE table my_lineitem_parq_partitioned
WITH (partitioned_by = ARRAY['l_shipdate']) AS
SELECT l_orderkey,
         l_partkey,
         l_suppkey,
         l_linenumber,
         l_quantity,
         l_extendedprice,
         l_discount,
         l_tax,
         l_returnflag,
         l_linestatus,
         l_commitdate,
         l_receiptdate,
         l_shipinstruct,
         l_comment,
         l_shipdate
FROM tpch100.lineitem_parq_partitioned
WHERE cast(l_shipdate as timestamp) < DATE('1992-02-01');

CREATE TABLE ctas_iceberg
WITH (
    table_type = 'ICEBERG',
    format = 'PARQUET',
    location = 's3://my_athena_results/ctas_iceberg_parquet/',
    is_external = false,
    partitioning = ARRAY['month(dt)'],
    vacuum_min_snapshots_to_keep = 10,
    vacuum_max_snapshot_age_ms = 259200
)
AS SELECT key1, name1, 'date' FROM table1;
