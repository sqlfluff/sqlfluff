{{ config(materialized='view') }}

with cte_example as (
     select 1 as col_name
),

final as
(
    select
        col_name,
        {{- echo('col_name') -}} as col_name2
    from
        cte_example
)

select * from final
