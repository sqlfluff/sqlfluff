CREATE MATERIALIZED VIEW mydataset.my_mv
AS REPLICA OF mydataset.my_original_mv;

CREATE MATERIALIZED VIEW my-project.mydataset.my_mv
OPTIONS(replication_interval_seconds=900)
AS REPLICA OF my-project.mydataset.my_original_mv;
