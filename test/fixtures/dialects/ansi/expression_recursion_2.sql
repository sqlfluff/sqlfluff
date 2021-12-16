 -- This test checks for recursion errors. If the expression
 -- is not parsed correctly it can lead to very deep recursion.

 -- If this test is failing, then check the structure of expression
 -- parsing.

 SELECT * FROM t WHERE a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b AND a < b
