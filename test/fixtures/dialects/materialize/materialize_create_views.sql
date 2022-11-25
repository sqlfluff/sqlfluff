
CREATE MATERIALIZED VIEW "test"."test" AS SELECT 1 AS "id";

CREATE VIEW "test"."test" AS SELECT 1 AS "id";

-- JSON parsing
CREATE MATERIALIZED VIEW "test"."test" AS SELECT '{"a": 1}'::json AS "id";
