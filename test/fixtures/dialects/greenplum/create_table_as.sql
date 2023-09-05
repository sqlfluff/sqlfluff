create table table1 (
    column1 int
    , column2 varchar
    , column3 boolean
)
with (appendoptimized = true, compresstype = zstd)
distributed by (column1, column2);

create table new_table as
select *
from old_table
distributed randomly;
