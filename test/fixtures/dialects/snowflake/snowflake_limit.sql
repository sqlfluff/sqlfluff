select c1 from testtable order by c1 limit 3;

select c1 from testtable order by c1 limit 3 offset 3;

select * from demo1 order by i limit null offset null;

select * from demo1 order by i limit '' offset '';

select * from demo1 order by i limit $$$$ offset $$$$;

select c1 from testtable order by c1 fetch 3;

select c1 from testtable order by c1 fetch first 3;

select c1 from testtable order by c1 fetch next 3;

select c1 from testtable order by c1 fetch 1 row;

select c1 from testtable order by c1 fetch 3 rows;

select c1 from testtable order by c1 fetch 3 only;

select c1 from testtable order by c1 offset 3 fetch 3;

select c1 from testtable order by c1 offset 1 row fetch 1 row;

select c1 from testtable order by c1 offset 3 rows fetch 3 rows;

select c1 from testtable offset 3 fetch 3;
