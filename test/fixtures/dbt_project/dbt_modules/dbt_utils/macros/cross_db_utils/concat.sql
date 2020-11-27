

{% macro concat(fields) -%}
  {{ adapter.dispatch('concat', packages = dbt_utils._get_utils_namespaces())(fields) }}
{%- endmacro %}

{% macro default__concat(fields) -%}
    concat({{ fields|join(', ') }})
{%- endmacro %}

{% macro alternative_concat(fields) %}
    {{ fields|join(' || ') }}
{% endmacro %}


{% macro redshift__concat(fields) %}
    {{ dbt_utils.alternative_concat(fields) }}
{% endmacro %}


{% macro snowflake__concat(fields) %}
    {{ dbt_utils.alternative_concat(fields) }}
{% endmacro %}
