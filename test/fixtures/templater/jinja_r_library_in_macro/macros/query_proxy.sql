{% macro query_proxy(tbl) %}SELECT 56
FROM {{ foo.schema }}.{{ foo.bar("xyz") }}
WHERE {{ bar.equals("x", 23) }}
{% endmacro %}
