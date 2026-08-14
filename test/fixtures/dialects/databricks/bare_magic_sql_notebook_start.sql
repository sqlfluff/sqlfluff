-- Databricks notebook source
%sql
SELECT a % 2 AS m FROM t;

-- COMMAND ----------

%python
print("opaque, not parsed as sql")

-- COMMAND ----------

%sql
SELECT b FROM u
