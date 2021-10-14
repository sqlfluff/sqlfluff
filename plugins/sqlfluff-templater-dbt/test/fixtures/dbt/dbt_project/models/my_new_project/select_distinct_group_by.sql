select distinct
    a,
    b,
    c
from table_a
{{ dbt_utils.group_by(3) }}
