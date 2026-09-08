-- one pair of brackets around the join target
select 1
from a
left join (b inner join c on true) on true;

-- two pairs
select 1
from a
left join ((b inner join c on true)) on true;

-- three pairs
select 1
from a
left join (((b inner join c on true))) on true;

-- a bracketed target that itself carries a trailing join
select 1
from a
left join ((b inner join c on true) inner join d on true) on true;

-- natural join with a bracketed target
select 1
from a
natural join ((b inner join c on true));
