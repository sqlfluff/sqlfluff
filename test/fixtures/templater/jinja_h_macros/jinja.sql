-- Spacing errors inside and outside of the macro.
-- This test make
select 1 + 2 + {{ bad_macro() }} + 999+101
from {{ very_long_table_name }}
