{% macro test_equality(model) %}


{#-- Prevent querying of db in parsing mode. This works because this macro does not create any new refs. #}
{%- if not execute -%}
    {{ return('') }}
{% endif %}

-- setup
{%- do dbt_utils._is_relation(model, 'test_equality') -%}

{#-
If the compare_cols arg is provided, we can run this test without querying the
information schema — this allows the model to be an ephemeral model
-#}
{%- if not kwargs.get('compare_columns', None) -%}
    {%- do dbt_utils._is_ephemeral(model, 'test_equality') -%}
{%- endif -%}

{% set compare_model = kwargs.get('compare_model', kwargs.get('arg')) %}
{% set compare_columns = kwargs.get('compare_columns', adapter.get_columns_in_relation(model) | map(attribute='quoted') ) %}
{% set compare_cols_csv = compare_columns | join(', ') %}

with a as (

    select * from {{ model }}

),

b as (

    select * from {{ compare_model }}

),

a_minus_b as (

    select {{compare_cols_csv}} from a
    {{ dbt_utils.except() }}
    select {{compare_cols_csv}} from b

),

b_minus_a as (

    select {{compare_cols_csv}} from b
    {{ dbt_utils.except() }}
    select {{compare_cols_csv}} from a

),

unioned as (

    select * from a_minus_b
    union all
    select * from b_minus_a

),

final as (

    select (select count(*) from unioned) +
        (select abs(
            (select count(*) from a_minus_b) -
            (select count(*) from b_minus_a)
            ))
        as count

)

select count from final

{% endmacro %}
