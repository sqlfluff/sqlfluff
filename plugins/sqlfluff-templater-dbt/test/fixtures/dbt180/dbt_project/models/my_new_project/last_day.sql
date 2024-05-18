with last_day_macro as (

select
    {{ dbt.last_day('2021-11-05', 'month') }}

)

select * from last_day_macro
