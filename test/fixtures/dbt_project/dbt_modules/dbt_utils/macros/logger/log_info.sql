{% macro log_info(message) %}

    {{ log(dbt_utils.pretty_log_format(message), info=True) }}

{% endmacro %}
