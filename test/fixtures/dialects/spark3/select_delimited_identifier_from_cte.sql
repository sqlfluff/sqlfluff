with `a``b!` as (
    select 1 as 0_identifier_1,
    random() as `100% questionable ``identifier`
),
0a as (
    select * from `a``b!`
)
select 0_identifier_1, `100% questionable ``identifier` from 0a;
