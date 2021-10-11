select
    a,
    coalesce(first_value(case when a then b else null end ignore nulls), false) as c
from d
