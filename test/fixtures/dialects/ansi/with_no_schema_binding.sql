create view my_schema.my_view as
select * from schema.table
with no schema binding;
