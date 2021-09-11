SELECT timestamp with time zone '2005-04-02 12:00:00-07' + interval '1 day';

SELECT DATEADD(day, -2, current_date);

SELECT timestamptz '2013-07-01 12:00:00' - timestamptz '2013-03-01 12:00:00';

SELECT 1.0::int;

select
    venuestate,
    venueseats,
    venuename,
    first_value(venuename ignore nulls)
    over(partition by venuestate
                      order by venueseats desc
        rows between unbounded preceding and unbounded following) as col_name
from table_name;
