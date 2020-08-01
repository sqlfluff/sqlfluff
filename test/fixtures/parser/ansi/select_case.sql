select
  case fruit_code
    when 0 then 'apple'
    when 1 then 'banana'
    when 2 then 'cashew'
  end as fruit
from some_table
