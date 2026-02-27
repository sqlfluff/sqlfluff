{%- if True %}
SELECT
    col_a AS foo
{%- else %}
select
    col_b as foo
{%- endif %}
FROM demo_table
{% if True %}
WHERE col_a BETWEEN 1 AND 2
{% else %}
where col_a between 2 and 3
{% endif %}
;
