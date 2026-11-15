ALTER EXTENSION hstore SET SCHEMA utils;
ALTER EXTENSION hstore ADD FUNCTION populate_record(anyelement, hstore);
ALTER EXTENSION "hstore" DROP TABLE public.ref_table;
ALTER EXTENSION hstore UPDATE TO '2.0';
ALTER EXTENSION repmgr UPDATE;
ALTER EXTENSION hstore ADD OPERATOR public.=== (box, box);
ALTER EXTENSION hstore ADD OPERATOR !! (NONE, integer);
ALTER EXTENSION hstore DROP OPERATOR !! (NONE, integer);
