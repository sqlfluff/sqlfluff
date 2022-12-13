
CREATE MATERIALIZED VIEW "test"."test" AS SELECT 1 AS "id";

CREATE VIEW "test"."test" AS SELECT 1 AS "id";

CREATE MATERIALIZED VIEW "test"."test" AS SELECT '{"a": 1}'::json AS "id";

CREATE MATERIALIZED VIEW active_customer_per_geo AS
    SELECT geo.name, count(*)
    FROM geo_regions AS geo
    JOIN active_customers ON active_customers.geo_id = geo.id
    GROUP BY geo.name;

CREATE MATERIALIZED VIEW active_customers AS
    SELECT guid, geo_id, last_active_on
    FROM customer_source
    GROUP BY geo_id;

CREATE VIEW purchase_sum_by_region
AS
    SELECT sum(purchase.amount) AS region_sum,
           region.id AS region_id
    FROM region
    INNER JOIN user
        ON region.id = user.region_id
    INNER JOIN purchase
        ON purchase.user_id = user.id
    GROUP BY region.id;

CREATE TEMP VIEW "test"."test" AS SELECT 1 AS "id";

CREATE TEMPORARY TABLE t (a int, b text NOT NULL);
