SELECT * FROM test1 INNER JOIN test2 ON test2.ty1=test1.ty1;
select tbl1.id from tbl1 as t1 inner join tbl2 as t2 on t1.id = t2.id;
select tbl1.id from tbl1 INNER ANY join tbl2 on tbl1.id = tbl2.id;

SELECT * FROM test1 CROSS JOIN test2;
select tbl1.id from tbl1 LEFT ANTI join tbl2 on tbl1.id = tbl2.id;
select tbl1.id from tbl1 RIGHT ANTI join tbl2 on tbl1.id = tbl2.id;

select tbl1.id from tbl1 LEFT ANY join tbl2 on tbl1.id = tbl2.id;
select tbl1.id from tbl1 RIGHT ANY join tbl2 on tbl1.id = tbl2.id;

select tbl1.id from tbl1 ASOF JOIN tbl2 on tbl1.id = tbl2.id;
select tbl1.id from tbl1 LEFT ASOF JOIN tbl2 on tbl1.id = tbl2.id;

select tbl1.id from tbl1 FULL JOIN tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 LEFT JOIN test2 USING ty1;

SELECT * FROM test1 ALL LEFT JOIN test2 USING ty1;
SELECT * FROM test1 ALL INNER ANY JOIN test2 USING (ty1,ty2);
SELECT * FROM test1 ALL FULL OUTER JOIN test2 USING ty1;
