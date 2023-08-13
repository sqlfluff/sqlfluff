-- Single table INSERT INTO

INSERT INTO foo (bar) VALUES(current_timestamp);

INSERT OVERWRITE INTO foo (bar) VALUES(current_timestamp);

INSERT INTO foo (bar, baz) VALUES(1, 2), (3, 4);

INSERT INTO foo (bar) VALUES(DEFAULT);

INSERT INTO foo (bar) VALUES(NULL);

INSERT INTO films SELECT * FROM tmp_films WHERE date_prod < '2004-05-07';

-- Unconditional multi-table INSERT INTO

insert all
  into t1
  into t1 (c1, c2, c3) values (n2, n1, default)
  into t2 (c1, c2, c3)
  into t2 values (n3, n2, n1)
select n1, n2, n3 from src;

insert overwrite all
  into t1
  into t1 (c1, c2, c3) values (n2, n1, default)
  into t2 (c1, c2, c3)
  into t2 values (n3, n2, n1)
select n1, n2, n3 from src;

insert all
  into t1 values ($1, an_alias, "10 + 20")
select 1, 50 as an_alias, 10 + 20;

insert all
  into t1 values (key, a)
select src1.key as key, src1.a as a
from src1, src2 where src1.key = src2.key;

-- Conditional multi-table INSERT INTO

insert all
  when n1 > 100 then
    into t1
  when n1 > 10 then
    into t1
    into t2
  else
    into t2
select n1 from src;

insert first
  when n1 > 100 then
    into t1
  when n1 > 10 then
    into t1
    into t2
  else
    into t2
select n1 from src;

insert all
  when c > 10 then
    into t1 (col1, col2) values (a, b)
select a, b, c from src;

INSERT INTO foo.bar
(
  SELECT
    foo.bar
);
