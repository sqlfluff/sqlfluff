-- Databricks notebook source

-- COMMAND ----------

-- A bare magic marker is only a magic command on the first line of a cell.

-- COMMAND ----------

%python
print("first line of the cell -> real magic cell")

-- COMMAND ----------

-- A `%keyword` that is NOT the first line of the cell is the modulo operator,
-- even when it starts a line and its right operand shares a magic keyword name.
SELECT
    a
    % r AS ratio,
    a
    %md AS still_modulo
FROM t
