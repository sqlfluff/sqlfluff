{{
    config(
        materialized='ephemeral',
    )
}}

SELECT * FROM
{{ ref('stg_creditview_products') }}
