select
  some_table.foo_id,
  array(
    select as struct *
    from another_table
    where another_table.foo_id = some_table.foo_id
  )
from another_table
