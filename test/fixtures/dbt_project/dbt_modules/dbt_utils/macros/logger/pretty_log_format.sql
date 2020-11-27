{% macro pretty_log_format(message) %}

    {{ return( dbt_utils.pretty_time() ~ ' + ' ~ message) }}

{% endmacro %}
