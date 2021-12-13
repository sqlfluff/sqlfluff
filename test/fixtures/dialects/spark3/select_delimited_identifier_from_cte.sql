with `a``b!` as (
    select 1 as _identifier_1,
    random() as `100% questionable ``identifier`
),
a0b as (
    select * from `a``b!`
)
select _identifier_1, `100% questionable ``identifier` from a0b;
