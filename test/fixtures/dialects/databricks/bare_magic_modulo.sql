-- Databricks notebook source

-- COMMAND ----------

%python
print("magic cell, not modulo")

-- COMMAND ----------

-- The `%` modulo operator must survive next to bare magic cells, even when the
-- right-hand operand shares a name with a magic keyword (r, md, sql, ...).
SELECT
    a % 2 AS m1,
    a%b AS m2,
    a%r AS m3,
    a%md AS m4
FROM t;
