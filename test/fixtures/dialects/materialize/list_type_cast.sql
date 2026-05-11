SELECT user_ids::uuid list AS user_id_list FROM testtable;
SELECT ARRAY[1, 2, 3]::int list AS int_list FROM t;
SELECT CAST(x AS int list) FROM t;