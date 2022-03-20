select cast(row(val1, val2) as row(a bigint, b varchar))
from sch.tbl;
