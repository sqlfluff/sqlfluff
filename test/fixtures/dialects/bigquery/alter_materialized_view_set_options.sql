ALTER MATERIALIZED VIEW mydataset.my_mv
SET OPTIONS (
    enable_refresh=false
);

ALTER MATERIALIZED VIEW mydataset.my_mv
SET OPTIONS (
    friendly_name="my_mv",
    labels=[("org_unit", "development")]
);
