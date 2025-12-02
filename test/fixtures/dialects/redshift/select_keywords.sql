SELECT pg_namespace.nspname AS constraint_schema, pg_constraint.conname AS constraint_name FROM pg_namespace, pg_constraint WHERE pg_namespace.oid = pg_constraint.connamespace;

-- As taken from: https://docs.aws.amazon.com/redshift/latest/dg/c_join_PG_examples.html
create view tables_vw as
select distinct(id) table_id
,trim(datname)   db_name
,trim(nspname)   schema_name
,trim(relname)   table_name
from stv_tbl_perm
join pg_class on pg_class.oid = stv_tbl_perm.id
join pg_namespace on pg_namespace.oid = relnamespace
join pg_database on pg_database.oid = stv_tbl_perm.db_id;
