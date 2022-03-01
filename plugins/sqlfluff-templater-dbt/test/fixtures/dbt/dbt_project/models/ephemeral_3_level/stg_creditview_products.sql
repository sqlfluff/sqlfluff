{{
    config(
        materialized='ephemeral',
    )
}}

SELECT * FROM
{{ ref('stg_max_product_contract_seats') }}
