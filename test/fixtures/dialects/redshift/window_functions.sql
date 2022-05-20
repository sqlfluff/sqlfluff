select
    lead(col1, 1) respect nulls over (order by col2 asc)
from dual
