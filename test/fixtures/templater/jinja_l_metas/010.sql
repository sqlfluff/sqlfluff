{% macro test_macro() %}
    SELECT 2;
{% endmacro %}

{{ test_macro() }}
