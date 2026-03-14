{%- if True %}
select
    col_a as foo
{%- else %}
select
    col_b as foo
{%- endif %}
from demo_table
{% if True %}
where col_a between 1 and 2
{% else %}
where col_a between 2 and 3
{% endif %}
;
