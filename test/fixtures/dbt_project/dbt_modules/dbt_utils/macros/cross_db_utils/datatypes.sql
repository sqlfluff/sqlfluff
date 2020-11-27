{# string  -------------------------------------------------     #}

{%- macro type_string() -%}
  {{ adapter.dispatch('type_string', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_string() %}
    string
{% endmacro %}

{%- macro redshift__type_string() -%}
    varchar
{%- endmacro -%}

{% macro postgres__type_string() %}
    varchar
{% endmacro %}

{% macro snowflake__type_string() %}
    varchar
{% endmacro %}



{# timestamp  -------------------------------------------------     #}

{%- macro type_timestamp() -%}
  {{ adapter.dispatch('type_timestamp', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_timestamp() %}
    timestamp
{% endmacro %}

{% macro snowflake__type_timestamp() %}
    timestamp_ntz
{% endmacro %}


{# float  -------------------------------------------------     #}

{%- macro type_float() -%}
  {{ adapter.dispatch('type_float', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_float() %}
    float
{% endmacro %}

{% macro bigquery__type_float() %}
    float64
{% endmacro %}

{# numeric  ------------------------------------------------     #}

{%- macro type_numeric() -%}
  {{ adapter.dispatch('type_numeric', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_numeric() %}
    numeric(28, 6)
{% endmacro %}

{% macro bigquery__type_numeric() %}
    numeric
{% endmacro %}


{# bigint  -------------------------------------------------     #}

{%- macro type_bigint() -%}
  {{ adapter.dispatch('type_bigint', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_bigint() %}
    bigint
{% endmacro %}

{% macro bigquery__type_bigint() %}
    int64
{% endmacro %}

{# int  -------------------------------------------------     #}

{%- macro type_int() -%}
  {{ adapter.dispatch('type_int', packages = dbt_utils._get_utils_namespaces())() }}
{%- endmacro -%}

{% macro default__type_int() %}
    int
{% endmacro %}

{% macro bigquery__type_int() %}
    int64
{% endmacro %}
