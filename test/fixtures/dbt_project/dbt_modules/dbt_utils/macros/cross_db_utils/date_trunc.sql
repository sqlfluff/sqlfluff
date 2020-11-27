{% macro date_trunc(datepart, date) -%}
  {{ adapter.dispatch('date_trunc', packages = dbt_utils._get_utils_namespaces()) (datepart, date) }}
{%- endmacro %}

{% macro default__date_trunc(datepart, date) %}
    date_trunc('{{datepart}}', {{date}})
{% endmacro %}

{% macro bigquery__date_trunc(datepart, date) %}
    timestamp_trunc(
        cast({{date}} as timestamp),
        {{datepart}}
    )

{% endmacro %}
