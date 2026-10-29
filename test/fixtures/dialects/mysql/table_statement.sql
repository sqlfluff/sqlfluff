table tbl;

table db1.tbl;

table tbl order by col1;

table tbl order by col1 desc limit 2;

table tbl limit 2 offset 1;

select 1, 2 union table tbl;

table tbl1 union all table tbl2 order by col1 limit 3;

select * from tbl1 where (col1, col2) in (table tbl2);

with cte as (table tbl) select * from cte;

create table tbl2 as table tbl;
