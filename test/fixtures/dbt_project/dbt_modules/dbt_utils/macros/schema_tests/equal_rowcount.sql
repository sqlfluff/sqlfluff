{% macro test_equal_rowcount(model) %}

{% set compare_model = kwargs.get('compare_model', kwargs.get('arg')) %}

{#-- Prevent querying of db in parsing mode. This works because this macro does not create any new refs. #}
{%- if not execute -%}
    {{ return('') }}
{% endif %}

with a as (

    select count(*) as count_a from {{ model }}

),
b as (

    select count(*) as count_b from {{ compare_model }}

),
final as (

    select abs(
            (select count_a from a) -
            (select count_b from b)
            )
        as diff_count

)

select diff_count from final

{% endmacro %}