select
    foo,
    case
        when
            bar is not null then bar
        else null
    end as test
from baz;
