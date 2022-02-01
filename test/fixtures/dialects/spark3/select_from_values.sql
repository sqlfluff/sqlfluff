select * from values 1;
select * from values (1);
select * from values (1,2);
select * from (values 1,2,3);
select * from (values (1),(2),(3));
select * from (values (1,2), (3,4));
select * from values 1, values 2;
select * from (values (1,2), (3,4)), (values (1,2), (3,4));
select * from (values 1, least(2,3), greatest(4,5));
select * from values 1 as t;
select * from values (1,2) as t(a, b);
select * from (values (1,2), (3,4)) as t (a, b);
select * from (values (1,2), (3,4)) as (a, b);
select * from values 1 t;
select * from values (1,2) t(a, b);
select * from (values (1,2), (3,4)) t (a, b);
select * from (values (1,2), (3,4)) (a, b);

-- TODO: These fail essentially because Delimited(Element) does not take the largest
-- possible Element, instead splitting on the first comma it reaches, see
-- https://github.com/sqlfluff/sqlfluff/issues/2427
-- select * from values 1 , 2
-- select * from values ( 1 , 2 ) , ( 3 , 4 )
-- select * from values 1 , 2 , values 3 , 4
-- select * from values (1) , (2)
-- select * from values 1 , 2 , values 3 , 4
