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
