-- Example of "select as struct *" syntax.
select
  some_table.foo_id,
  array(
    select as struct *
    from another_table
    where another_table.foo_id = some_table.foo_id
  )
from another_table;

-- Example of "select as struct <<column list>>" syntax
select as struct
  '1' as bb,
  2 as aa;

-- Example of explicitly building a struct in a select clause.
select
  struct(
    bar.bar_id as id,
    bar.bar_name as bar
  ) as bar
from foo
left join bar on bar.foo_id = foo.foo_id;
