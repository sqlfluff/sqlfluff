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
