select
    col1,
    col2
from some_table
qualify row_number() over (partition by col1 order by col1) = 1
union all
select
    col1,
    col2
from some_table
qualify row_number() over (partition by col1 order by col1) = 1
