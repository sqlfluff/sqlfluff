-- https://github.com/sqlfluff/sqlfluff/issues/780

{{
  config(
    materialized = 'incremental',
    unique_key='product_id'
    )
}}

select
    {#- Attributes #}
    products.product_id,
    products.valid_date_local,
    products._fivetran_deleted
from products
inner join dispensaries
where not products._fivetran_deleted
{% if is_incremental() -%}
    and products.valid_date_local >= (
        select max(valid_date_local) from {{ this }})
{% endif %}
