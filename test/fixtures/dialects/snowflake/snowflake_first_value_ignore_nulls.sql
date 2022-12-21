select
    a,
    coalesce(first_value(case when a then b else null end) ignore nulls over (order by e), false) as c
from d
