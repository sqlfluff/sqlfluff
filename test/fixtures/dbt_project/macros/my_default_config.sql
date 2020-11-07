-- Issue #335
{% macro my_default_config(type) %}
    {{ config(materialized="view") }}
{% endmacro %}
