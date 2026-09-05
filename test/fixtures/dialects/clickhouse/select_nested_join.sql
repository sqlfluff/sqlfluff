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

-- redundant brackets in the FROM clause, which parsed before #8382 and must
-- keep the tree they had
select 1
from ((a inner join b on true));

-- a join after the inner bracket
select 1
from a
left join ((b inner join c on true) left join d on true) on true;
