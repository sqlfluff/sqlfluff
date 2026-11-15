select
    state,
    city
from sales
order by all;

select
    state,
    city
from sales
order by all desc;

select
    state,
    city
from sales
order by all nulls last;

select
    state,
    city
from sales
order by all asc nulls first
limit 10;
