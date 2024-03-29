-- no type join
SELECT * FROM test1 ALL JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 ANY JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL ALL JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL ANY JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL JOIN test2 ON test2.ty1=test1.ty1;
-- INNER join
SELECT * FROM test1 INNER JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL INNER JOIN test2 ON test2.ty1=test1.ty1;
-- INNER join ...
SELECT * FROM test1 INNER ALL JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 INNER ANY JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL INNER ALL JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL INNER ANY JOIN test2 ON test2.ty1=test1.ty1;
-- ... INNER join
SELECT * FROM test1 ALL INNER JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 ANY INNER JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL ALL INNER JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL ANY INNER JOIN test2 ON test2.ty1=test1.ty1;
-- LEFT JOIN
SELECT * FROM test1 LEFT JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL LEFT JOIN test2 ON test2.ty1=test1.ty1;
-- LEFT join ...
SELECT tbl1.id FROM tbl1 LEFT ANTI join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 LEFT SEMI JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ANY JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ALL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ASOF JOIN test2 USING ty1,ty2;
SELECT tbl1.id FROM tbl1 GLOBAL LEFT ANTI join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 GLOBAL LEFT SEMI JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ANY JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ALL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ASOF JOIN test2 USING ty1,ty2;
-- ... LEFT join
select tbl1.id from tbl1  ANTI LEFT join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 SEMI LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 ANY LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 ALL LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 ASOF LEFT JOIN test2 USING (ty1,ty2);
select tbl1.id from tbl1  GLOBAL ANTI LEFT join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 GLOBAL SEMI LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL ANY LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL ALL LEFT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL ASOF LEFT JOIN test2 USING (ty1,ty2);
-- LEFT join test case OUTER
SELECT * FROM test1 as t1 LEFT OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ASOF OUTER JOIN test2 USING ty1,ty2;
SELECT tbl1.id FROM tbl1 LEFT ANTI OUTER join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 LEFT SEMI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ANY OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ALL OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 LEFT ASOF OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ASOF OUTER JOIN test2 USING ty1,ty2;
SELECT tbl1.id FROM tbl1 GLOBAL LEFT ANTI OUTER join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 GLOBAL LEFT SEMI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ANY OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ALL OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL LEFT ASOF OUTER JOIN test2 USING ty1,ty2;
-- RIGHT JOIN
SELECT * FROM test1 RIGHT JOIN test2 ON test2.ty1=test1.ty1;
SELECT * FROM test1 GLOBAL RIGHT JOIN test2 ON test2.ty1=test1.ty1;
-- RIGHT join ...
SELECT tbl1.id FROM tbl1 RIGHT ANTI join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 RIGHT SEMI JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT ANY JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT ALL JOIN test2 USING ty1,ty2;
SELECT tbl1.id FROM tbl1 GLOBAL RIGHT ANTI join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 GLOBAL RIGHT SEMI JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT ANY JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT ALL JOIN test2 USING ty1,ty2;
-- ... RIGHT join
select tbl1.id from tbl1  ANTI RIGHT join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 SEMI RIGHT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 ANY RIGHT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 ALL RIGHT JOIN test2 USING ty1,ty2;
select tbl1.id from tbl1  GLOBAL ANTI RIGHT join tbl2 on tbl1.id = tbl2.id;
SELECT * FROM test1 as t1 GLOBAL SEMI RIGHT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL ANY RIGHT JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL ALL RIGHT JOIN test2 USING ty1,ty2;
-- RIGHT join test case OUTER
SELECT * FROM test1 as t1 RIGHT OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT ANTI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT SEMI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT ANY OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 RIGHT ALL OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT ANTI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT SEMI OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT ANY OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL RIGHT ALL OUTER JOIN test2 USING ty1,ty2;
-- ASOF join
select tbl1.id from tbl1 ASOF JOIN tbl2 on tbl1.id = tbl2.id;
select tbl1.id from tbl1 GLOBAL ASOF JOIN tbl2 on tbl1.id = tbl2.id;
-- CROSS join
SELECT * FROM test1 CROSS JOIN test2;
SELECT * FROM test1 GLOBAL CROSS JOIN test2;
-- FULL join
SELECT * FROM test1 as t1 FULL ALL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 FULL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 FULL ALL OUTER JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL FULL ALL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL FULL JOIN test2 USING ty1,ty2;
SELECT * FROM test1 as t1 GLOBAL FULL ALL OUTER JOIN test2 USING ty1,ty2;
-- PASTE join
SELECT * FROM table1 t1 PASTE JOIN table2 t2;
SELECT * FROM table1 t1 GLOBAL PASTE JOIN table2 t2;
-- ARRAY join
SELECT col FROM (SELECT arr FROM test1) AS t2 ARRAY JOIN arr AS col;
SELECT col FROM (SELECT [1, 2] AS arr) AS t1 LEFT ARRAY JOIN arr AS col;
SELECT * FROM (SELECT [1, 2] AS arr) AS t1 ARRAY JOIN arr;
SELECT * FROM (SELECT [1, 2] AS arr) AS t1 LEFT ARRAY JOIN arr;
SELECT * FROM (SELECT [1, 2] AS arr, [3, 4] AS arr2) AS t1 ARRAY JOIN arr, arr2;
SELECT x, y FROM (SELECT [1, 2] AS arr, [3, 4] AS arr2) AS t1 ARRAY JOIN arr AS x, arr2 AS y;
SELECT *,ch,cg FROM (SELECT 1) ARRAY JOIN ['1','2'] as cg, splitByChar(',','1,2') as ch;
SELECT * FROM (SELECT [1,2] x) AS t1 ARRAY JOIN t1.*;
