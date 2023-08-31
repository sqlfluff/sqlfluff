create table t1 as (
select *
from t2
)
distributed randomly;

create table t1 as
    select *
    from t2;
