{%- if True %}
SELECT
    col_a AS foo
{%- else %}
SELECT
    col_b AS foo
{%- endif %}
FROM demo_table
{% if True %}
WHERE col_a BETWEEN 1 AND 2
{% else %}
WHERE col_a BETWEEN 2 AND 3
{% endif %}
;
