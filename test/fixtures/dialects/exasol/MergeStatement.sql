MERGE INTO staff T
USING changes U
ON T.name = U.name
WHEN MATCHED THEN UPDATE SET T.salary = U.salary,
                                T.lastChange = CURRENT_DATE
                    WHERE T.salary < U.salary
WHEN NOT MATCHED THEN INSERT VALUES (U.name,U.salary,CURRENT_DATE);
----
MERGE INTO staff T
USING (SELECT name FROM X) U
ON T.name = U.name
WHEN MATCHED THEN DELETE;
---
MERGE INTO staff T
USING (SELECT name FROM X) U
ON T.name = U.name
WHEN NOT MATCHED THEN INSERT VALUES (1,2,3)
WHEN MATCHED THEN DELETE;
