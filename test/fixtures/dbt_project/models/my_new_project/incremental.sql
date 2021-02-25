-- https://github.com/sqlfluff/sqlfluff/issues/780
-- Note we don't call is_incremental directly in the test
-- because that requires a database connection.

select
    {#- Attributes #}
    products.product_id,
    products._fivetran_deleted
from products
inner join dispensaries
where not products._fivetran_deleted
{% if true -%}
and products.valid_date_local >= (select max(valid_date_local) from {{ this }})
{% endif -%}