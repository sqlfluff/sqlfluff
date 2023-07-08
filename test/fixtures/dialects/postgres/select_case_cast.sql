select
    col0,
    case
        when col1
        then col2
        else col3
    end::text as mycol
from table1;

select
    col0,
    case
        when col1
        then col2
        else col3
    end::int::float as mycol
from table1;

select
    col0,
    cast(case
        when col1
        then col2
        else col3
    end as text) as mycol
from table1;
