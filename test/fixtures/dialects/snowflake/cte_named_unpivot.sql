with src as (
    select 1 as july
),

unpivot as (
    select *
    from src
    unpivot(budget for month_name in (july))
)

select * from unpivot;
