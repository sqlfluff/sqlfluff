-- 1. Column distinctness in SELECT expression
-- TODO allow this to work without brackets
SELECT (a_column IS DISTINCT FROM b_column) FROM t_table;
SELECT (b_column IS NOT DISTINCT FROM c_column) FROM t_table;

-- 2. Column distinctness in WHERE expression
SELECT a_column FROM t_table WHERE a_column IS DISTINCT FROM b_column;
SELECT a_column FROM t_table WHERE a_column IS NOT DISTINCT FROM b_column;

-- 3. Column distinctness in JOIN expression
SELECT t_table_1.a_column
FROM t_table_1
INNER JOIN t_table_2
    ON t_table_1.a_column IS DISTINCT FROM t_table_2.a_column;
SELECT t_table_1.a_column
FROM t_table_1
INNER JOIN t_table_2
    ON t_table_1.a_column IS NOT DISTINCT FROM t_table_2.a_column;

-- 4. Column distinctness in MERGE expression
MERGE INTO t_table_1
USING t_table_2
ON t_table_1.a_column IS DISTINCT FROM t_table_2.a_column
WHEN NOT MATCHED THEN INSERT (a) VALUES (b);
MERGE INTO t_table_1
USING t_table_2
ON t_table_1.a_column IS NOT DISTINCT FROM t_table_2.a_column
WHEN NOT MATCHED THEN INSERT (a) VALUES (b);
