UPDATE t1
SET a = SUBSTR(REPLACE(CAST(gen_random_uuid() AS VARCHAR(32)), '-',''),1,16)
WHERE a in (SELECT a
                        FROM t1
                        GROUP BY a
                        HAVING SUM(1)>1);
