SELECT * REPLACE (CAST(1 AS BOOLEAN) AS foo) FROM (SELECT 1 AS foo);

-- Single replace
select
  * replace ('thing' as foo)
from some_table;

-- Multi replace
select
  * REPLACE (quantity/2 AS quantity, 'thing' as foo)
from some_table
