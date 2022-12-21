-- Start of the week the date belongs to
{% macro week_start_date(date) -%}

date_trunc('week', CONVERT_TIMEZONE( 'UTC', 'America/New_York',  {{date}} ) )

{% endmacro %}
