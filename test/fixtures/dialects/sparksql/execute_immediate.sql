-- https://spark.apache.org/docs/latest/sql-ref-syntax-aux-exec-imm.html

EXECUTE IMMEDIATE 'SELECT SUM(c1) FROM VALUES(?), (?) AS t(c1)' USING 5, 6;

EXECUTE IMMEDIATE sqlStr;

EXECUTE IMMEDIATE sqlStr USING arg1, arg2;

EXECUTE IMMEDIATE sqlStr INTO sum;

EXECUTE IMMEDIATE sqlStr INTO sum USING arg1, arg2;

EXECUTE IMMEDIATE 'SELECT id, name FROM tbl WHERE id = ?' INTO b, a USING 10;

EXECUTE IMMEDIATE 'CREATE TEMPORARY VIEW IDENTIFIER(:tblName) AS SELECT 1'
USING 'tbl_view_tmp' AS tblName;

-- The reference makes AS optional, and Spark's own tests use lower case.
EXECUTE IMMEDIATE 'REFRESH TABLE IDENTIFIER(:tblName)' USING 'x' as tblName;

-- "For compatibility with other SQL dialects, EXECUTE IMMEDIATE also supports
-- USING ( { arg_expr [ AS ] [alias] } [, ...] )"
EXECUTE IMMEDIATE sqlStr USING (limitA AS limitA);

EXECUTE IMMEDIATE sqlStr INTO sum USING (5 AS first, arg2 AS second);

-- A constant expression, not only a literal or a variable.
EXECUTE IMMEDIATE 'SELECT ' || func || '(c1) FROM VALUES(:first) AS t(c1)'
USING 5 + 7 AS first, length('hello') AS second;
