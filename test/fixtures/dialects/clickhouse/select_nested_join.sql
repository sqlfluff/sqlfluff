-- redundant brackets around a join used as a join target
-- https://github.com/sqlfluff/sqlfluff/issues/8382
select 1
from a
left join (b inner join c on true) on true;

select 1
from a
left join ((b inner join c on true)) on true;

select 1
from a
left join (((b inner join c on true))) on true;
