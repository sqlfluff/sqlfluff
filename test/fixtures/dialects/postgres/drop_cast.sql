-- ANSI SQL:

DROP CAST (int AS bool);

DROP CAST (int AS bool) RESTRICT;

DROP CAST (int AS bool) CASCADE;

DROP CAST (udt_1 AS udt_2);

DROP CAST (sch.udt_1 AS sch.udt_2);

-- Additional PG extensions:

DROP CAST IF EXISTS (int AS bool);
DROP CAST IF EXISTS (int AS bool) RESTRICT;
DROP CAST IF EXISTS (int AS bool) CASCADE;
