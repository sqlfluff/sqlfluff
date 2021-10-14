
select
    {%- for col in dbt_utils.get_column_values(
        table=ref("select_distinct_group_by"),
        column="ids"
    ) %}
    {{ col }}{{ "," if not loop.last }}
    {%- endfor %}
from table_a
