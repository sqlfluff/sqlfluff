{% macro safe_cast(field, type) %}
  {{ adapter.dispatch('safe_cast', packages = dbt_utils._get_utils_namespaces()) (field, type) }}
{% endmacro %}


{% macro default__safe_cast(field, type) %}
    {# most databases don't support this function yet
    so we just need to use cast #}
    cast({{field}} as {{type}})
{% endmacro %}


{% macro snowflake__safe_cast(field, type) %}
    try_cast({{field}} as {{type}})
{% endmacro %}


{% macro bigquery__safe_cast(field, type) %}
    safe_cast({{field}} as {{type}})
{% endmacro %}
