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
    products._fivetran_deleted,
    dispensaries.id
from products
inner join dispensaries
    on
        products.dispensary_id = dispensaries.dispensary_id
        and products.valid_date_local = dispensaries.valid_date_local
where not products._fivetran_deleted
{% if is_incremental() -%}
    and products.valid_date_local >= (
        select max(valid_date_local) from {{ this }})
{% endif %}
