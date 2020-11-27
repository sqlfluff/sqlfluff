{% macro length(expression) -%}
    {{ adapter.dispatch('length', packages = dbt_utils._get_utils_namespaces()) (expression) }}
{% endmacro %}


{% macro default__length(expression) %}
    
    length(
        {{ expression }}
    )
    
{%- endmacro -%}


{% macro redshift__length(expression) %}

    len(
        {{ expression }}
    )
    
{%- endmacro -%}