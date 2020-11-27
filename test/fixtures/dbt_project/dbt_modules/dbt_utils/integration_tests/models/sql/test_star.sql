
-- TODO : Should the star macro use a case-insensitive comparison for the `except` field on Snowflake?

{% set exclude_field = 'FIELD_3' if target.type == 'snowflake' else 'field_3' %}


with data as (

    select
        {{ dbt_utils.star(from=ref('data_star'), except=[exclude_field]) }}

    from {{ ref('data_star') }}

)

select * from data
