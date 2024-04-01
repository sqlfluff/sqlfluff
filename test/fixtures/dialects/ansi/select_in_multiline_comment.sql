with a as (

    select *
    from table_a

),

/*
    select
*/

b as (

    select *
    from a

)

select *
from b
