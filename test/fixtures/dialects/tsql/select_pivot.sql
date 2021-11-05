select [1], [2], [3]
from
    table1 as t1
pivot
    (max(value) for rn in ([1], [2], [3]) ) as pvt;

select [1], [2], [3]
from
    table1 as t1
pivot
    (max(value) for rn in ([1], [2], [3]) ) pvt;
