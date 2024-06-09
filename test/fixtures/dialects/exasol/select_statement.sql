SELECT last_name, employee_id id, manager_id mgr_id,
    CONNECT_BY_ISLEAF leaf, LEVEL,
    LPAD(' ', 2*LEVEL-1)||SYS_CONNECT_BY_PATH(last_name, '/') "PATH"
FROM employees
CONNECT BY PRIOR employee_id = manager_id AND dept_no = dno
START WITH last_name = 'Clark'
ORDER BY employee_id;
----
SELECT store, SUM(price) AS volume FROM sales GROUP BY store ORDER BY store DESC;
----
SELECT name, SUM(price) AS volume FROM customers JOIN sales USING (c_id)
GROUP BY name ORDER BY name;
----
WITH tmp_view AS
    (SELECT name, price, store FROM customers, sales
        WHERE customers.c_id=sales.c_id)
SELECT sum(price) AS volume, name, store FROM tmp_view
GROUP BY GROUPING SETS (name,store,());
----
SELECT * FROM (IMPORT INTO (v VARCHAR(1))
FROM EXA AT my_connection TABLE sys.dual);
----
SELECT aschema.afunction('hello', 123) FROM aschema.mytable
WHERE (a,2,substr(c,1,3)) IN (SELECT a,b,c FROM bschema.yourtable);
----
WITH mylist AS (
    VALUES ('a','b','c'), ('d','e','f'), (f1('a'),'b','d')
    AS mylist (a,b,c)
)
SELECT * from mylist;
----
SELECT
rowid,
ROW_NUMBER () OVER (
    PARTITION BY (
        col1,
        col2
    )
    ORDER BY
        col1 DESC,
        col2 DESC
);
----
SELECT
rowid,
ROW_NUMBER () OVER (
    PARTITION BY (
        col1,
        col2
    ))
ORDER BY
    col1 DESC,
    col2 DESC;
----
SELECT x WITH INVALID UNIQUE(myid) FROM t;
----
SELECT * FROM values('x', 'y');
----
SELECT * FROM values('x', 'y') AS x(c1,c2);
----
SELECT * FROM values(('x','2'), ('y','2')) AS x(c1,c2);
----
SELECT * FROM(VALUES 1,2,3);
----
SELECT * FROM(VALUES 1,2,3) AS xs(n1);
----
SELECT * FROM VALUES BETWEEN 1 AND 15 WITH STEP 4;
----
SELECT first_name,name WITH INVALID FOREIGN KEY (nr) from T1
REFERENCING T2 (id);
----
SELECT * WITH INVALID FOREIGN KEY (first_name,name) from T1
REFERENCING T2;
----
SELECT INVALID FOREIGN KEY (nr,first_name,name) from T1
REFERENCING T2 (id, first_name,name);
----
SELECT * INTO TABLE t2 FROM t1 ORDER BY 1;
----
SELECT date'2021-09-21' FROM dual;
----
SELECT INVALID PRIMARY KEY (first_name) from T1;
----
SELECT  JSON_EXTRACT(json_str, '$."@id"', '$.error()')
        EMITS
        (
            id VARCHAR(2000),
            error_column VARCHAR(2000000)
        )
FROM t;
----
SELECT 10 / 2;
----
select count(*) as a, local.a*10 from x;
----
SELECT ABS(x) AS x FROM t WHERE local.x>10;
----
SELECT c1 as cx, count(*) as cc FROM x GROUP BY local.cx;
----
SELECT c1 as cx FROM x ORDER BY local.cx;
----
SELECT c1, count(*) as c FROM x GROUP BY 1 HAVING local.c > 1;
----
SELECT S_ID, C_ID, PRICE, ROW_NUMBER() OVER (PARTITION BY C_ID ORDER BY PRICE DESC) NUM FROM SALES QUALIFY local.NUM = 1;
SELECT [day] FROM T;
----
SELECT "day" FROM T;
----
SELECT * FROM T PREFERRING HIGH LOCAL.ranking PARTITION BY local.c1;
----
SELECT * FROM T PREFERRING HIGH LOCAL.ranking PRIOR TO LOW LOCAL.budget PARTITION BY local.c1;
----
SELECT * FROM T PREFERRING HIGH LOCAL.ranking PLUS LOW LOCAL.budget PARTITION BY local.c1;
----
SELECT * FROM T PREFERRING HIGH LOCAL.ranking PRIOR TO LOW LOCAL.budget INVERSE col20 PARTITION BY local.c1;
----
SELECT * FROM T WHERE (LOCAL.c1, LOCAL.c2) NOT IN  (SELECT c1,c2 FROM  b);
----
SELECT 'ABC' as c1 FROM dual WHERE local.c1 = 'ABC';
SELECT a, b, c FROM x
union
SELECT a, b, c FROM y
ORDER BY a;
----
SELECT -1 * row_number() OVER() AS nummer
FROM sys.exa_sql_keywords
CROSS JOIN sys.exa_sql_keywords
UNION ALL
SELECT 0;
--
SELECT
	INTERVAL '5' MONTH,
	INTERVAL '130' MONTH (3),
	INTERVAL '27' YEAR,
	INTERVAL '100-1' YEAR(3) TO MONTH,
	INTERVAL '2-1' YEAR TO MONTH,
	INTERVAL '10:20' HOUR TO MINUTE,
	INTERVAL '2 23:10:59' DAY TO SECOND,
	INTERVAL '6' MINUTE,
	INTERVAL '5' DAY ,
	INTERVAL '100' HOUR(3) ,
	INTERVAL '1.99999' SECOND(2,2) ,
	INTERVAL '23:10:59.123' HOUR(2) TO SECOND(3);
--
SELECT v,
       DATE'2020-10-26' + v * INTERVAL'7'DAY AS late_2020_mondays,
       5 * v AS five_times_table
FROM VALUES BETWEEN 1 AND 9 AS v(v);
--
SELECT 'abcd' LIKE 'a_d' AS res1, '%bcd' like '%%d' AS res2;
--
SELECT 'abcd' NOT LIKE 'a_d' AS res1, '%bcd' like '%%d' AS res2;
--
SELECT 'My mail address is my_mail@exasol.com'
       REGEXP_LIKE '(?i).*[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}.*'
       AS contains_email;
--
SELECT 'My mail address is my_mail@exasol.com'
       NOT REGEXP_LIKE '(?i).*[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}.*'
       AS contains_email;
--
SELECT current_date -1 as dt from dual;
