-- We can call functions when replacing a field
select
  * except(foo)
    replace (concat(fruit, 'berry') as fruit)
from some_table
