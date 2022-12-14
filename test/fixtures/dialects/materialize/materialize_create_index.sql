
CREATE INDEX active_customers_geo_idx ON active_customers (geo_id);

CREATE INDEX active_customers_exp_idx ON active_customers (upper(guid));

CREATE INDEX i2 IN CLUSTER cluster2 ON t1 (f1);
