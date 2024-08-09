-- sqlfluff:render_variant_limit:10
select
    a,
    {% if 1 > 2 %}
        B,
    {% elif 3 > 1 %}
        C,
    {% else %}
        D,
    {% endif %}
    d
from e
