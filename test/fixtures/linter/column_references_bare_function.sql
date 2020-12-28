select
    ta.column_a,
    current_timestamp as column_b,
    tb.column_c
from table_a as ta
join table_b as tb
    using(id)
