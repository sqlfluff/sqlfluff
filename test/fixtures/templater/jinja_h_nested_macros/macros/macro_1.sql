{% macro config_wrapper(type) %}
    {{ dbt_config(materialized = "view") }}
{% endmacro %}
