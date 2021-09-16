select d.*, r.* except(date_key)
from my_table as d
inner join my_other_table as r using(date_key)
