with util_days_macro as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="'2020-06-01'",
        end_date="'2021-01-01'"
    ) }}

)

select * from util_days_macro
