select
    venuestate,
    venueseats,
    venuename,
    first_value(venuename ignore nulls)
    over(partition by venuestate
                      order by venueseats desc
        rows between unbounded preceding and unbounded following) as col_name
from table_name;

SELECT rank () OVER (ORDER BY my_column RANGE BETWEEN 12 FOLLOWING AND CURRENT ROW EXCLUDE NO OTHERS);

SELECT rank () OVER (ORDER BY my_column GROUPS UNBOUNDED PRECEDING EXCLUDE GROUP);

SELECT rank () OVER (ORDER BY my_column RANGE BETWEEN
        INTERVAL '1 YEAR - 1 DAYS' PRECEDING AND
        INTERVAL '15 DAYS' PRECEDING);

-- Frame clauses without ORDER BY
SELECT sum(x) OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) FROM t;

SELECT sum(x) OVER (ROWS UNBOUNDED PRECEDING) FROM t;

SELECT sum(x) OVER (RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) FROM t;

SELECT sum(x) OVER (PARTITION BY y ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) FROM t;
