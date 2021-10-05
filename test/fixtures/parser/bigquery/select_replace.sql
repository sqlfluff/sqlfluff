-- Single replace
select
  * replace 'thing' as foo
from some_table;

-- Multi replace
select
  * REPLACE (quantity/2 AS quantity, 'thing' as foo)
from some_table
