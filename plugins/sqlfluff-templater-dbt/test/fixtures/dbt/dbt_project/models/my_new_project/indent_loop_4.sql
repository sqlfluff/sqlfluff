-- This file tests the indentation of line 6, which isn't rendered on the last pass.
select
    a,
    {%- for i in range(1, 3) -%}
        1 as b_{{ i }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
from {{ source("jaffle_shop", "orders") }}
