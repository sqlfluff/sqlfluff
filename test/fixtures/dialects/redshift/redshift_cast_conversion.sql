select cast(col1 as integer)
from tbl1;

select convert(integer, col1)
from tbl1;

select col1::integer
from tbl1;

select cast(col1 as timestamptz)
from tbl1;

select convert(timestamptz, col1)
from tbl1;

select col1::timestamptz
from tbl1;

select cast(col1 as decimal(38, 2))
from tbl1;

select convert(decimal(38, 2), col1)
from tbl1;

select col1::decimal(38, 2)
from tbl1;

select cast(col1 as interval)
from tbl1;

select convert(interval, col1)
from tbl1;

select col1::interval
from tbl1;
