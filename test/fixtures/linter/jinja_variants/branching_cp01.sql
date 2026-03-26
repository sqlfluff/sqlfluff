-- sqlfluff:render_variant_limit:6
-- sqlfluff:rules:capitalisation.keywords:capitalisation_policy:upper
select
    {% if True %}
        a as foo
    {% else %}
        b as foo
    {% endif %}
from example_table
{% if False %}
where col_one between 1 and 2
{% elif True %}
where col_one between 2 and 3
{% else %}
where col_one between 3 and 4
{% endif %}
