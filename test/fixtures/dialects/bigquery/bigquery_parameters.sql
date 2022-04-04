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
