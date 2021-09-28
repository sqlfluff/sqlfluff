with my_cte as (
    select 1
)
, that_cte as (
    select 1
),
-- This Comment should stick to the CTE
other_cte as (
    select 1
),
this_cte as (select 1), final_cte as (
    select 1
) select * from my_cte cross join other_cte
