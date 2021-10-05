--bigquery allows for named params like @param or ordered params in ?
select "1" from x where y = @z_test1;
select datetime_trunc(@z2, week);
select datetime_trunc(@_ab, week);
select datetime_trunc(@a, week);
select "1" from x where y = ?;
select concat("1", ?);
