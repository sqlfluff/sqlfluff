select * ilike 'col_%' from table1;

select t.* ilike '%suffix' from table1 as t;

select
    * ilike 'col_%',
    1 as one,
    b.* ilike '%some%'
from a
left join b on a.id = b.id;

select * ilike 'col_%' replace (1 as col1) from table1;

select * ilike 'col_%' replace (1 as col1) rename col1 as col2 from table1;
