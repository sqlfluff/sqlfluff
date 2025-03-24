select *
from tbl
where int_col in (1, 2);

select *
from tbl
where int_col in [1, 2];

select *
from tbl
where int_col global in (1, 2);

select *
from tbl
where int_col not in [toUUID('a'), toUUID('b')];
