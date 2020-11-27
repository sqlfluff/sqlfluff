/*
This function has been tested with dateparts of month and quarters. Further
testing is required to validate that it will work on other dateparts.
*/

{% macro last_day(date, datepart) %}
  {{ adapter.dispatch('last_day', packages = dbt_utils._get_utils_namespaces()) (date, datepart) }}
{% endmacro %}


{%- macro default_last_day(date, datepart) -%}
    cast(
        {{dbt_utils.dateadd('day', '-1',
        dbt_utils.dateadd(datepart, '1', dbt_utils.date_trunc(datepart, date))
        )}}
        as date)
{%- endmacro -%}


{% macro default__last_day(date, datepart) -%}
    {{dbt_utils.default_last_day(date, datepart)}}
{%- endmacro %}


{% macro postgres__last_day(date, datepart) -%}

    {%- if datepart == 'quarter' -%}
    {{ exceptions.raise_compiler_error(
        "dbt_utils.last_day is not supported for datepart 'quarter' on this adapter") }}
    {%- else -%}
    {{dbt_utils.default_last_day(date, datepart)}}
    {%- endif -%}

{%- endmacro %}
