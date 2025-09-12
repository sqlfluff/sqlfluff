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

select cast(pg_namespace.nspname as information_schema.sql_identifier)
from pg_namespace;

select col1::"varchar"
from tbl1;

select
    col1::"text",
    col2::"varchar"
from tbl1;

select null::"varchar" as col1;

select
    null::"varchar" as col1,
    null::varchar as col2;

select
    'test'::"varchar" as col1,
    'test2'::"text" as col2;
