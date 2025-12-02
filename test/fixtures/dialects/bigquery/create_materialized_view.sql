CREATE MATERIALIZED VIEW mydataset.my_mv
AS SELECT * FROM anotherdataset.mv_base_table;

CREATE MATERIALIZED VIEW IF NOT EXISTS mydataset.my_mv
AS SELECT * FROM anotherdataset.mv_base_table;

CREATE MATERIALIZED VIEW mydataset.my_mv
OPTIONS(
    friendly_name="my_mv"
)
AS SELECT * FROM anotherdataset.mv_base_table;

CREATE MATERIALIZED VIEW mydataset.my_mv
PARTITION BY DATE(x)
CLUSTER BY y
AS SELECT x, y
FROM anotherdataset.mv_base_table;
