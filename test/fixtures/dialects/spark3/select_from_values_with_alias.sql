select a, b from values (1, 2) as (a,b);
select a, b from values (1, 2) as t(a,b);
select a, b from values (1, 2) t(a,b);
select a, b from values (1, 2) (a,b);
select a, b from values (1, 2), (3, 4) as (a,b);
select a, b from values (1, 2), (3, 4) as t(a,b);
select a, b from values (1, 2), (3, 4) t(a,b);
select a, b from values (1, 2), (3, 4) (a,b);
