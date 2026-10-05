--bigquery allows for named params like @param or ordered params in ?
select "1" from x where y = @z_test1;
select datetime_trunc(@z2, week);
select datetime_trunc(@_ab, week);
select datetime_trunc(@a, week);
select parse_date("%Y%m", year); -- this should parse year as an identifier
select "1" from x where y = ?;
select concat("1", ?);

select
    id,
    datetime_trunc(@z2, week),
    sum(something) over( partition by some_id order by some_date rows BETWEEN @query_parameter PRECEDING AND CURRENT ROW) as some_sum
from some_table
where some_column = @query_parameter2;

-- A datetime unit used as one of several arguments to a function which does not
-- take date parts is a column reference, whatever the function is called.
select my_udf(year, 1), my_udf(day, month) from t;
