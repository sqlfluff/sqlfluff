with (select (1, 2, 3)) as in_arr_cte
select *
from tbl
where int_col in in_arr_cte;

with (1, 2, 3) as int_arr
select *
from tbl
where int_col in int_arr;

with [1, 2, 3] as int_arr
select *
from tbl
where int_col in int_arr;

with [1, 2, 3] as int_arr
select *,
       if(int_col in int_arr, 1, 0) as in_array_flag
from tbl;
