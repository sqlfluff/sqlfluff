ALTER EXTENSION hstore SET SCHEMA utils;
ALTER EXTENSION hstore ADD FUNCTION populate_record(anyelement, hstore);
ALTER EXTENSION "hstore" DROP TABLE public.ref_table;
ALTER EXTENSION hstore UPDATE TO '2.0';
ALTER EXTENSION repmgr UPDATE;
