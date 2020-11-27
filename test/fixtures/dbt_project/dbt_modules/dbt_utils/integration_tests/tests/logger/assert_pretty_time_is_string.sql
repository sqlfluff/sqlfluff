{% if dbt_utils.pretty_time() is string %}
    {# Return 0 rows for the test to pass #}
    select 1 limit 0
{% else %}
    {# Return >0 rows for the test to fail #}
    select 1
{% endif %}
