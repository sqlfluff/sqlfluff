{% set cols = ["a", "b", "b"] %}

select
    {% for col in cols %}
    {{ col }}
from table_a
