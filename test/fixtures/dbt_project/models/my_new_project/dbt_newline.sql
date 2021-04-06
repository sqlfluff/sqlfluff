with

orders as (
    select *
    from {{ source("jaffle_shop", "orders") }}
)

select
    a, b,
    c,
    count(*) as occurences
/*
This identation violation is aritificially included to test dbt trailing
newline fucntionality when 'exclude_rules = L009'. There needs to be a fixable
violation present in the raw SQL for the dbt templater to compile the SQL so we
insert one here.
*/
    from orders  -- Line indented for testing purposes. Trailing newline after.
