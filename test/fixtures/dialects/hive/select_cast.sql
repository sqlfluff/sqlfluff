select
    cast(row(col1, col2) as row(a bigint, b decimal(23, 2)))
from sch.tbl;

select cast(a as json)
from sch.tbl;
