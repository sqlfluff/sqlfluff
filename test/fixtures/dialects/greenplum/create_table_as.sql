create temp table tester
with (appendoptimized = true, compresstype = zstd) as
select
    column_1
    , column_2
    , column_3 as last_column
from schema.another_table
where column_1 = 'test'
distributed by (column_2, last_column);

create table schema.a_new_table as
select *
from schema.old_table
distributed randomly;
